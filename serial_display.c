#include <stdio.h>   /* Standard input/output definitions */
#include <string.h>  /* String function definitions */
#include <unistd.h>  /* UNIX standard function definitions */
#include <fcntl.h>   /* File control definitions */
#include <errno.h>   /* Error number definitions */
#include <termios.h> /* POSIX terminal control definitions */

#define ERROR		//Display error messages
//#define DEBUG		//Display debug messages
//#define DISPLAY "/dev/cuaU1"
#define DISPLAY "/dev/cu.usbserial-A900frrf"

void process_buffer(int displayfd, char *loc, int *size);
void write_to_display(int displayfd, char *loc, int size);

/*
 * 'open_port()' - Open serial port 1.
 *
 * Returns the file descriptor on success or -1 on error.
 */

int open_port(char *device) {
	int fd; /* File descriptor for the port */
	fd = open(device, O_RDWR | O_NOCTTY );
	if (fd == -1) {
		/*
		* Could not open the port.
		*/
		#ifdef ERROR
		fprintf(stdout, "open_port: Unable to open %s\n",device);
		#endif
	} else {
		fcntl(fd, F_SETFL, 0);
		#ifdef DEBUG
		fprintf(stdout, "open_port: Opened %s\n",device);
		#endif
	}

	return (fd);
}

void set_baud(int fd) {
	struct termios options;

	/*
	 * Get the current options for the port...
	 */

	tcgetattr(fd, &options);

	/*
	 * Set the baud rates to 57600...
	 */

	cfsetispeed(&options, B57600);
	cfsetospeed(&options, B57600);

	/*
	 * Enable the receiver and set local mode...
	 */

	options.c_cflag |= (CLOCAL | CREAD);

	/*
	 * Disable echo
	 */
	//cflag = control options
	options.c_cflag &= ~(ECHO | ECHOE | PARENB | CSTOPB | CSIZE);
	options.c_cflag |= (CS8);
	//lflag = line options
	options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
	//iflag = input options
	options.c_iflag &= ~(IXON| IXOFF| IXANY);
	//oflag = output optinos
	options.c_oflag &= ~OPOST;
	//minimum # to read is 0
	options.c_cc[VMIN] = 0;
	//time to wait for data is 100/10=10 seconds
	options.c_cc[VTIME] = 100;
	/*
	 * Set the new options for the port...
	 */

	tcsetattr(fd, TCSANOW, &options);
}

int main(int argc, char **argv) {
	int displayfd,filefd,n,size,i;
	char buffer[255], *loc;

	displayfd=open_port(DISPLAY);
	if (displayfd==-1) {
		return 1;
	}
	set_baud(displayfd);
	//Wait for arduino to be ready (sends OK when ready);
	//read will block until display is ready
	n=read(displayfd,buffer,sizeof(char)*3);
	if (n>0) {
		buffer[n]='\0';
		#ifdef DEBUG
		fprintf(stdout, "Display ready with: %s\n",buffer);
		#endif
	} else {
		#ifdef ERROR
		buffer[n]='\0';
		fprintf(stdout, "Display not ready.\n");
		#endif
		return 1;
	}

	if (argc>1) {
		//If user supplied string arguments, print them then leave	
		for (i=1; i<argc; i++) {
			size=strlen(argv[i]);
			n=write(displayfd,argv[i],size);
			if (n < 0) {
				#ifdef ERROR
				fprintf(stdout, "write() of %s, %d chars failed\n",argv[i],size);
				#endif
			} else {
				#ifdef DEBUG
				fprintf(stdout, "wrote %s, %d chars to displayfd\n",argv[i],n);
				#endif
			}
		}
	} else {
		//We're reading indefinitely from stdin
		//Useful for sending data from shellscript/program
		//into the serial display
		i=0;
		//while (fgets(buffer, sizeof(buffer), stdin)!=NULL) {
		while ((n=read(STDIN_FILENO, buffer, sizeof(char)*254))>0) {
			//leave original buffer intact, so copy pointer to it
			//and change our local pointer around
			loc=&buffer[0];
			loc[n]='\0';
			size=strlen(loc);
			#ifdef DEBUG
			fprintf(stdout, "Read %d chars; strlen is %d\n",n,size);
			#endif
			
			process_buffer(displayfd, loc, &size);
		}
	}
	//Close display file descriptor
	close(displayfd);
	//All done
	return 0;
}

void write_to_display(int displayfd, char *loc, int size) {
	int n=0;

	#ifdef DEBUG
	fprintf(stdout,"size=%d, loc=%d, loc=%s\n",size,loc[0],loc);
	#endif
	if (size<=0 || (size==1 && loc[0]==48)) {
		#ifdef DEBUG
		fprintf(stdout, "loc size is %d, loc=%s\n",size,loc);
		#endif
		return;
	}
	n=write(displayfd,loc,size);
	if (n < 0) {
		#ifdef ERROR
		fprintf(stdout, "write() of %s, %d chars failed\n",loc,size);
		#endif
		return;
	} else {
		#ifdef DEBUG
		fprintf(stdout, "wrote %s, %d chars to displayfd\n",loc,n);
		#endif
	}
}

void process_buffer(int displayfd, char *loc, int *size) {
	int i;

	// Check for control codes, and only send it if found
	if (loc[0]==27) {
		//Set display brightness
		//0-3 0=100%, 1=75%, 2=50%, 3=25%
		loc[2]='\0';
		*size=strlen(loc);
		#ifdef DEBUG
		fprintf(stdout,"Got char %d, brightness set to %d\n",loc[0],loc[1]);
		#endif
		write_to_display(displayfd, loc, *size);
		loc=&loc[3];
		*size=strlen(loc);
		if (*size) {
			#ifdef DEBUG
			fprintf(stdout,"%d Chars remain, going again.\n",*size);
			#endif
			process_buffer(displayfd, loc, size);
		}
	} else if (loc[0]==28) {
		//Clear display
		loc[1]='\0';
		*size=strlen(loc);
		#ifdef DEBUG
		fprintf(stdout,"Got char %d!\n",loc[0]);
		#endif
		write_to_display(displayfd, loc, *size);
		loc=&loc[2];
		process_buffer(displayfd, loc, size);
		if (*size) {
			#ifdef DEBUG
			fprintf(stdout,"%d Chars remain, going again.\n",*size);
			#endif
			process_buffer(displayfd, loc, size);
		}
	} else if (loc[0]==29) {
		//Set scrolling speed (update delay in 10's of ms)
		//Only allow 1 char for speed setting
		//0-254 = 0-2.54 seconds delay
		loc[2]='\0';
		*size=strlen(loc);
		#ifdef DEBUG
		fprintf(stdout,"Got char %d, speed set to %d\n",loc[0],loc[1]);
		#endif
		write_to_display(displayfd, loc, *size);
		loc=&loc[3];
		process_buffer(displayfd, loc, size);
		if (*size) {
			#ifdef DEBUG
			fprintf(stdout,"%d Chars remain, going again.\n",*size);
			#endif
			process_buffer(displayfd, loc, size);
		}
	} else if (loc[0]==30) {
		//Tell display new first line data is coming
		loc[1]='\0';
		*size=strlen(loc);
		#ifdef DEBUG
		fprintf(stdout,"Got char %d!\n",loc[0]);
		#endif
		write_to_display(displayfd, loc, *size);
		loc=&loc[2];
		process_buffer(displayfd, loc, size);
		if (*size) {
			#ifdef DEBUG
			fprintf(stdout,"%d Chars remain, going again.\n",*size);
			#endif
			process_buffer(displayfd, loc, size);
		}
	} else if (loc[0]==31) {
		//Tell display new second line data is coming
		loc[1]='\0';
		*size=strlen(loc);
		#ifdef DEBUG
		fprintf(stdout,"Got char %d!\n",loc[0]);
		#endif
		write_to_display(displayfd, loc, *size);
		loc=&loc[2];
		*size=strlen(loc);
		if (*size) {
			#ifdef DEBUG
			fprintf(stdout,"%d Chars remain, going again.\n",*size);
			#endif
			process_buffer(displayfd, loc, size);
		}
	} else {
		//Remove newlines in string; replace with space,
		//or end string early if at end
		for (i=0; i<*size; i++) {
			if (loc[i]=='\n') {
				if (i==*size-1) {
					loc[i]='\0';
				} else {
					loc[i]=' ';
				}
			}
		}
		//Update size (may have changed)
		*size=strlen(loc);
		//remove empty space/newlines at beginning of string
		if (*size<2 && loc[0]==' ') {
			loc[0]='\0';
		}

		//Update size
		*size=strlen(loc);
		write_to_display(displayfd, loc, *size);
		loc=&loc[*size];
		*size=strlen(loc);
		if (*size) {
			#ifdef DEBUG
			fprintf(stdout,"%d Chars remain, going again.\n",*size);
			#endif
			process_buffer(displayfd, loc, size);
		}
	}
}

