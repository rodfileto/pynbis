/*******************************************************************************
Minimal AN2K stub header for PyNBIS compilation
This provides minimal type definitions and constants needed by NBIS
*******************************************************************************/

#ifndef _AN2K_H
#define _AN2K_H

/* Constants */
#define MM_PER_INCH                 25.4

/* Forward declarations for ANSI/NIST types */
/* These are only needed if using to_type9 functions */
typedef struct record RECORD;
typedef struct ansi_nist ANSI_NIST;
typedef struct field FIELD;

#endif /* !_AN2K_H */
