git#include <stdio.h>
#include <string.h>
#include <stdlib.h>


typedef struct {
        int pageNo;
        int modified;
} page;
enum    repl { rand_repl, fifo, lru, clock};
int     createMMU( int);
int     checkInMemory( int ) ;
int     allocateFrame( int ) ;
page    selectVictim( int, enum repl) ;
const   int pageoffset = 12;            /* Page size is fixed to 4 KB */

int     numFrames ;
typedef struct {
	int pageNo;
	int frameNo;
	int valid;      // 1 if in memory, 0 if not
	int modified;   // dirty bit
} page_table_entry;

typedef struct {
	int pageNo;     // -1 if free
	int modified;   // dirty bit
	int last_access_time;  // For LRU tracking
	int reference_bit;     // For Clock algorithm
} frame_table_entry;

page_table_entry *page_table = NULL;
frame_table_entry *frame_table = NULL;
int max_pages = 1 << (32 - 12); // 32-bit address space, 4KB pages
int allocated = 0;
int access_counter = 0;  // Global counter for LRU tracking
int clock_hand = 0;      // Clock hand position for Clock algorithm

/* Creates the page table structure to record memory allocation */
int     createMMU (int frames)
{
	numFrames = frames;  // Ensure global variable matches parameter
	
	// Allocate and initialize page table and frame table
	page_table = (page_table_entry*)malloc(sizeof(page_table_entry) * max_pages);
	if (!page_table) return -1;
	for (int i = 0; i < max_pages; i++) {
		page_table[i].pageNo = i;
		page_table[i].frameNo = -1;
		page_table[i].valid = 0;
		page_table[i].modified = 0;
	}
	frame_table = (frame_table_entry*)malloc(sizeof(frame_table_entry) * frames);
	if (!frame_table) return -1;
	for (int i = 0; i < frames; i++) {
		frame_table[i].pageNo = -1;
		frame_table[i].modified = 0;
		frame_table[i].last_access_time = 0;
		frame_table[i].reference_bit = 0;
	}
	allocated = 0;
	return 0;
}

/* Checks for residency: returns frame no or -1 if not found */
int     checkInMemory( int page_number)
{
	int result = -1;
	if (page_number < 0 || page_number >= max_pages) return -1;
	if (page_table[page_number].valid) {
		result = page_table[page_number].frameNo;
		// Update access time for LRU tracking
		access_counter++;
		frame_table[result].last_access_time = access_counter;
		// Set reference bit for Clock algorithm
		frame_table[result].reference_bit = 1;
	}
	return result;
}

/* allocate page to the next free frame and record where it put it */
int     allocateFrame( int page_number)
{
	// Find a free frame
	for (int i = 0; i < numFrames; i++) {
		if (frame_table[i].pageNo == -1) {
		frame_table[i].pageNo = page_number;
		frame_table[i].modified = 0;
		access_counter++;
		frame_table[i].last_access_time = access_counter;
		frame_table[i].reference_bit = 1;
			page_table[page_number].frameNo = i;
			page_table[page_number].valid = 1;
			page_table[page_number].modified = 0;
			return i;
		}
	}
	// No free frame found (should not happen if called correctly)
	return -1;
}

/* Selects a victim for eviction/discard according to the replacement algorithm,  returns chosen frame_no  */
page    selectVictim(int page_number, enum repl  mode )
{
	page victim;
	
	if (mode == rand_repl) {
		int victim_frame = rand() % numFrames;
		int victim_page = frame_table[victim_frame].pageNo;
		victim.pageNo = victim_page;
		victim.modified = frame_table[victim_frame].modified;
		// Invalidate victim in page table
		page_table[victim_page].valid = 0;
		page_table[victim_page].frameNo = -1;
		// Replace with new page
		frame_table[victim_frame].pageNo = page_number;
		frame_table[victim_frame].modified = 0;
		page_table[page_number].frameNo = victim_frame;
		page_table[page_number].valid = 1;
		page_table[page_number].modified = 0;
		return victim;
	}

	else if (mode == lru) {
		// Find frame with smallest (oldest) last_access_time
		int oldest_time = frame_table[0].last_access_time;
		int victim_frame = 0;
		
		for (int i = 1; i < numFrames; i++) {
			if (frame_table[i].last_access_time < oldest_time) {
				oldest_time = frame_table[i].last_access_time;
				victim_frame = i;
			}
		}
		
		int victim_page = frame_table[victim_frame].pageNo;
		victim.pageNo = victim_page;
		victim.modified = frame_table[victim_frame].modified;
		
		// Invalidate victim in page table
		page_table[victim_page].valid = 0;
		page_table[victim_page].frameNo = -1;
		
		// Replace with new page
		frame_table[victim_frame].pageNo = page_number;
		frame_table[victim_frame].modified = 0;
		access_counter++;
		frame_table[victim_frame].last_access_time = access_counter;
		page_table[page_number].frameNo = victim_frame;
		page_table[page_number].valid = 1;
		page_table[page_number].modified = 0;
		
		return victim;
	}
	
	else if (mode == clock) {
		// Clock algorithm: find first frame with reference bit 0
		int start_hand = clock_hand;
		int victim_frame = -1;
		
		// First pass: look for frame with reference bit 0
		do {
			if (frame_table[clock_hand].reference_bit == 0) {
				victim_frame = clock_hand;
				break;
			} else {
				// Clear reference bit and move to next frame
				frame_table[clock_hand].reference_bit = 0;
			}
			clock_hand = (clock_hand + 1) % numFrames;
		} while (clock_hand != start_hand);
		
		// If no frame found with reference bit 0, use current position
		if (victim_frame == -1) {
			victim_frame = clock_hand;
		}
		
		int victim_page = frame_table[victim_frame].pageNo;
		victim.pageNo = victim_page;
		victim.modified = frame_table[victim_frame].modified;
		
		// Invalidate victim in page table
		page_table[victim_page].valid = 0;
		page_table[victim_page].frameNo = -1;
		
		// Replace with new page
		frame_table[victim_frame].pageNo = page_number;
		frame_table[victim_frame].modified = 0;
		frame_table[victim_frame].reference_bit = 1;
		access_counter++;
		frame_table[victim_frame].last_access_time = access_counter;
		page_table[page_number].frameNo = victim_frame;
		page_table[page_number].valid = 1;
		page_table[page_number].modified = 0;
		
		// Move clock hand to next position
		clock_hand = (clock_hand + 1) % numFrames;
		
		return victim;
	}
	
	// Default: return dummy (for unimplemented algorithms)
	victim.pageNo = 0;
	victim.modified = 0;
	return victim;
}

		
int main(int argc, char *argv[])
{
  
	char	*tracename;
	int	page_number,frame_no, done ;
	int	do_line;
	int	no_events, disk_writes, disk_reads;
	int     debugmode;
 	enum	repl  replace;
        unsigned address;
    	char 	rw;
	page	Pvictim;
	FILE	*trace;


        if (argc < 5) {
             printf( "Usage: ./memsim inputfile numberframes replacementmode debugmode \n");
             exit ( -1);
	}
	else {
        tracename = argv[1];	
	trace = fopen( tracename, "r");
	if (trace == NULL ) {
             printf( "Cannot open trace file %s \n", tracename);
             exit ( -1);
	}
	numFrames = atoi(argv[2]);
        if (numFrames < 1) {
            printf( "Frame number must be at least 1\n");
            exit ( -1);
        }
		if (strcmp(argv[3], "lru\0") == 0)
			replace = lru;
		else if (strcmp(argv[3], "rand\0") == 0)
			replace = rand_repl;
		else if (strcmp(argv[3], "clock\0") == 0)
			replace = clock;
		else if (strcmp(argv[3], "fifo\0") == 0)
			replace = fifo;
        else 
	  {
             printf( "Replacement algorithm must be rand/fifo/lru/clock  \n");
             exit ( -1);
	  }

        if (strcmp(argv[4], "quiet\0") == 0)
            debugmode = 0;
	else if (strcmp(argv[4], "debug\0") == 0)
            debugmode = 1;
        else 
	  {
             printf( "Replacement algorithm must be quiet/debug  \n");
             exit ( -1);
	  }
	}
	
	done = createMMU (numFrames);
	if ( done == -1 ) {
		 printf( "Cannot create MMU" ) ;
		 exit(-1);
        }
	no_events = 0 ;
	disk_writes = 0 ;
	disk_reads = 0 ;

        do_line = fscanf(trace,"%x %c",&address,&rw);
	while ( do_line == 2)
	{
		page_number =  address >> pageoffset;
		frame_no = checkInMemory( page_number) ;    /* ask for physical address */

		if ( frame_no == -1 )
		{
		  disk_reads++ ;			/* Page fault, need to load it into memory */
		  if (debugmode) 
		      printf( "Page fault %8d \n", page_number) ;
		  if (allocated < numFrames)  			/* allocate it to an empty frame */
		   {
                     frame_no = allocateFrame(page_number);
		     allocated++;
                   }
                   else{
		      Pvictim = selectVictim(page_number, replace) ;   /* returns page number of the victim  */
		      frame_no = checkInMemory( page_number) ;    /* find out the frame the new page is in */
		   if (Pvictim.modified)           /* need to know victim page and modified  */
	 	      {
                      disk_writes++;			    
                      if (debugmode) printf( "Disk write %8d \n", Pvictim.pageNo) ;
		      }
		   else
                      if (debugmode) printf( "Discard    %8d \n", Pvictim.pageNo) ;
		   }
		}
		if ( rw == 'R'){
		    if (debugmode) printf( "reading    %8d \n", page_number) ;
		}
		else if ( rw == 'W'){
			// mark page in page table and frame table as written - modified
			if (page_table[page_number].valid) {
				page_table[page_number].modified = 1;
				int frame = page_table[page_number].frameNo;
				if (frame >= 0 && frame < numFrames) {
					frame_table[frame].modified = 1;
				}
			}
			if (debugmode) printf( "writting   %8d \n", page_number) ;
		}
		 else {
		      printf( "Badly formatted file. Error on line %d\n", no_events+1); 
		      exit (-1);
		}

		no_events++;
        	do_line = fscanf(trace,"%x %c",&address,&rw);
	}

	printf( "total memory frames:  %d\n", numFrames);
	printf( "events in trace:      %d\n", no_events);
	printf( "total disk reads:     %d\n", disk_reads);
	printf( "total disk writes:    %d\n", disk_writes);
	printf( "page fault rate:      %.4f\n", (float) disk_reads/no_events);
}
				
