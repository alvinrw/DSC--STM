/*
 * dsc_rome_16b.h
 *
 *  Created on: Sep 29, 2020
 *      Author: RDN
 */

#ifndef DSC_ROME_16B_H_
#define DSC_ROME_16B_H_

#define to_digital(x)	(uint16_t)(((float)x*65535.0)/360.0)
#define to_syncro(x)	((float)x*360.0)/65535.0
#define digital_to_degree(x)	((float)x)  // Digital (0-360) sama dengan derajat

float syncro_value(float data);
void dsc(float degree);
float mirror_value(float data);
#endif /* DSC_ROME_16B_H_ */
