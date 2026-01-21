#include "main.h"

void dsc(uint16_t digital){
  // Add delay for DSC converter to latch data (needed for motor synchro!)
  HAL_Delay(10);
  
  //bit 0
  if(digital&0x0001){
    HAL_GPIO_WritePin(B1_GPIO_Port, B1_Pin, SET);
  }
  else HAL_GPIO_WritePin(B1_GPIO_Port, B1_Pin, RESET);

  //bit 1
  if(digital&0x0002){
    HAL_GPIO_WritePin(B2_GPIO_Port, B2_Pin, SET);
  }
  else HAL_GPIO_WritePin(B2_GPIO_Port, B2_Pin, RESET);

  //bit 2
  if(digital&0x0004){
    HAL_GPIO_WritePin(B3_GPIO_Port, B3_Pin, SET);
  }
  else HAL_GPIO_WritePin(B3_GPIO_Port, B3_Pin, RESET);

  //bit 3
  if(digital&0x0008){
    HAL_GPIO_WritePin(B4_GPIO_Port, B4_Pin, SET);
  }
  else HAL_GPIO_WritePin(B4_GPIO_Port, B4_Pin, RESET);

  //bit 4
  if(digital&0x0010){
    HAL_GPIO_WritePin(B5_GPIO_Port, B5_Pin, SET);
  }
  else HAL_GPIO_WritePin(B5_GPIO_Port, B5_Pin, RESET);

  //bit 5
  if(digital&0x0020){
    HAL_GPIO_WritePin(B6_GPIO_Port, B6_Pin, SET);
  }
  else HAL_GPIO_WritePin(B6_GPIO_Port, B6_Pin, RESET);

  //bit 6
  if(digital&0x0040){
    HAL_GPIO_WritePin(B7_GPIO_Port, B7_Pin, SET);
  }
  else HAL_GPIO_WritePin(B7_GPIO_Port, B7_Pin, RESET);

  //bit 7
  if(digital&0x0080){
    HAL_GPIO_WritePin(B8_GPIO_Port, B8_Pin, SET);
  }
  else HAL_GPIO_WritePin(B8_GPIO_Port, B8_Pin, RESET);

  //bit 8
  if(digital&0x0100){
    HAL_GPIO_WritePin(B9_GPIO_Port, B9_Pin, SET);
  }
  else HAL_GPIO_WritePin(B9_GPIO_Port, B9_Pin, RESET);

  //bit 9
  if(digital&0x0200){
    HAL_GPIO_WritePin(B10_GPIO_Port, B10_Pin, SET);
  }
  else HAL_GPIO_WritePin(B10_GPIO_Port, B10_Pin, RESET);

  //bit 10
  if(digital&0x0400){
    HAL_GPIO_WritePin(B11_GPIO_Port, B11_Pin, SET);
  }
  else HAL_GPIO_WritePin(B11_GPIO_Port, B11_Pin, RESET);

  //bit 11
  if(digital&0x0800){
    HAL_GPIO_WritePin(B12_GPIO_Port, B12_Pin, SET);
  }
  else HAL_GPIO_WritePin(B12_GPIO_Port, B12_Pin, RESET);

  //bit 12
  if(digital&0x1000){
    HAL_GPIO_WritePin(B13_GPIO_Port, B13_Pin, SET);
  }
  else HAL_GPIO_WritePin(B13_GPIO_Port, B13_Pin, RESET);

  //bit 13
  if(digital&0x2000){
    HAL_GPIO_WritePin(B14_GPIO_Port, B14_Pin, SET);
  }
  else HAL_GPIO_WritePin(B14_GPIO_Port, B14_Pin, RESET);

  //bit 14
  if(digital&0x4000){
    HAL_GPIO_WritePin(B15_GPIO_Port, B15_Pin, SET);
  }
  else HAL_GPIO_WritePin(B15_GPIO_Port, B15_Pin, RESET);

  //bit 15
  if(digital&0x8000){
    HAL_GPIO_WritePin(B16_GPIO_Port, B16_Pin, SET);
  }
  else HAL_GPIO_WritePin(B16_GPIO_Port, B16_Pin, RESET);
  
  // Add delay after GPIO write for stability (needed for motor synchro!)
  HAL_Delay(10);
}

float syncro_value(float data){
	if(data < 0)return data+=360;
	else if (data >=360) return data -=360;
	else return data;
}
float mirror_value(float data){
	return syncro_value(360-data);
}

