/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2020 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f1xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "ssd1306.h"
#include "fonts.h"
#include "stdio.h"
#include "dsc_rome_16b.h"
/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

// ============================================
// DEVICE ID CONFIGURATION
// Change this for each STM32 device (1-5)
// ============================================
#define DEVICE_ID 2  // Device 1, 2, 3, 4, or 5

// Protocol definitions
#define SERIAL_DIST_MARKER  0xBB
#define SERIAL_PACKET_SIZE  4

#define len_uart1	20  // Buffer untuk ASCII text input
/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */
struct UART_RX{
	float buffer_sync;
	char text_buffer[90];  // Buffer untuk ASCII text (15-byte broadcast needs ~80 chars)
	uint8_t text_index;
};
typedef struct UART_RX MY_UART;

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define LED_BLINK_Pin GPIO_PIN_13
#define LED_BLINK_GPIO_Port GPIOC
#define EN_SYNC_Pin GPIO_PIN_14
#define EN_SYNC_GPIO_Port GPIOC
#define B1_Pin GPIO_PIN_0
#define B1_GPIO_Port GPIOA
#define B2_Pin GPIO_PIN_1
#define B2_GPIO_Port GPIOA
#define B3_Pin GPIO_PIN_2
#define B3_GPIO_Port GPIOA
#define B4_Pin GPIO_PIN_3
#define B4_GPIO_Port GPIOA
#define B5_Pin GPIO_PIN_4
#define B5_GPIO_Port GPIOA
#define B6_Pin GPIO_PIN_5
#define B6_GPIO_Port GPIOA
#define B7_Pin GPIO_PIN_6
#define B7_GPIO_Port GPIOA
#define B8_Pin GPIO_PIN_7
#define B8_GPIO_Port GPIOA
#define B14_Pin GPIO_PIN_10
#define B14_GPIO_Port GPIOB
#define B15_Pin GPIO_PIN_11
#define B15_GPIO_Port GPIOB
#define B9_Pin GPIO_PIN_8
#define B9_GPIO_Port GPIOA
#define B10_Pin GPIO_PIN_9
#define B10_GPIO_Port GPIOA
#define B11_Pin GPIO_PIN_10
#define B11_GPIO_Port GPIOA
#define B12_Pin GPIO_PIN_11
#define B12_GPIO_Port GPIOA
#define B13_Pin GPIO_PIN_12
#define B13_GPIO_Port GPIOA
#define B16_Pin GPIO_PIN_15
#define B16_GPIO_Port GPIOA
#define PB_UP_Pin GPIO_PIN_3
#define PB_UP_GPIO_Port GPIOB
#define PB_DOWN_Pin GPIO_PIN_4
#define PB_DOWN_GPIO_Port GPIOB
/* USER CODE BEGIN Private defines */
extern float syncro_val;
/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
