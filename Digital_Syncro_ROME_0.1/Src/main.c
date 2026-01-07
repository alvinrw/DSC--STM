/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
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
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdlib.h>  // untuk atoi()
#include <string.h>  // untuk memset()
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
 I2C_HandleTypeDef hi2c1;

UART_HandleTypeDef huart1;
DMA_HandleTypeDef hdma_usart1_rx;

/* USER CODE BEGIN PV */
MY_UART MY_UART1;

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_I2C1_Init(void);
static void MX_DMA_Init(void);
static void MX_USART1_UART_Init(void);
/* USER CODE BEGIN PFP */
float syncro_val=0;
uint16_t digital_val=0;  // Nilai digital input (0-360)
uint8_t dsc_mode=1;
// 0 -> roll
// 1 -> pitch
// 2 -> yaw
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */
	char txt[30];
	uint8_t length;
	float sync_lcd;
  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_I2C1_Init();
  MX_DMA_Init();
  MX_USART1_UART_Init();
  /* USER CODE BEGIN 2 */
  HAL_Delay(100);
  
  // Inisialisasi buffer untuk UART
  MY_UART1.text_index = 0;
  memset(MY_UART1.text_buffer, 0, sizeof(MY_UART1.text_buffer));
  
  // Inisialisasi nilai
  digital_val = 0;
  syncro_val = 0.0;
  
  // Init OLED dengan delay lebih lama
  HAL_Delay(200);
  SSD1306_Init();
  HAL_Delay(100);
  
  SSD1306_GotoXY(10,0);
  SSD1306_Puts("Digital Syncro", &Font_7x10, 1);
  SSD1306_UpdateScreen();
  HAL_Delay(50);
  
  SSD1306_GotoXY(10,10);
  SSD1306_Puts("Digital: 0   ", &Font_7x10, 1);
  SSD1306_UpdateScreen();
  HAL_Delay(50);
  
  SSD1306_GotoXY(10,30);
  SSD1306_Puts("Syncro: 0.00  ", &Font_7x10, 1);
  SSD1306_UpdateScreen();
  HAL_Delay(50);
  
  SSD1306_GotoXY(5,50);
  SSD1306_Puts("Send via Serial", &Font_7x10, 1);
  SSD1306_UpdateScreen();
  HAL_Delay(50);
  
  // Init GPIO output
  dsc(0);
  
  // Kirim pesan awal via UART
  sprintf(txt, "STM32 Ready - Send 0-360\\r\\n");
  HAL_UART_Transmit(&huart1, (uint8_t*)txt, strlen(txt), 100);
  
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
	  // Polling UART - Terima 1 byte
	  uint8_t received_char;
	  if(HAL_UART_Receive(&huart1, &received_char, 1, 100) == HAL_OK){
		  // Jika terima angka (0-9), simpan ke buffer
		  if(received_char >= '0' && received_char <= '9'){
			  if(MY_UART1.text_index < 19){
				  MY_UART1.text_buffer[MY_UART1.text_index] = received_char;
				  MY_UART1.text_index++;
			  }
		  }
		  // Jika terima newline, proses data
		  else if(received_char == '\n' || received_char == '\r'){
			  if(MY_UART1.text_index > 0){
				  // Null-terminate
				  MY_UART1.text_buffer[MY_UART1.text_index] = '\0';
				  
				  // Konversi ke integer
				  int value = atoi(MY_UART1.text_buffer);
				  
				  // Validasi range
				  if(value < 0) value = 0;
				  if(value > 360) value = 360;
				  
				  // Update nilai
				  digital_val = (uint16_t)value;
				  syncro_val = (float)value;
				  
				  // Update OLED
				  SSD1306_GotoXY(10,10);
				  sprintf(txt, "Digital: %d   ", digital_val);
				  SSD1306_Puts(txt, &Font_7x10, 1);
				  
				  SSD1306_GotoXY(10,30);
				  sprintf(txt, "Syncro: %.2f  ", syncro_val);
				  SSD1306_Puts(txt, &Font_7x10, 1);
				  
				  SSD1306_UpdateScreen();
				  
				  // Output ke GPIO
				  dsc(syncro_val);
				  
				  // Kirim konfirmasi balik ke Python
				  sprintf(txt, "OK: Digital=%d, Syncro=%.2f\r\n", digital_val, syncro_val);
				  HAL_UART_Transmit(&huart1, (uint8_t*)txt, strlen(txt), 100);
				  
				  // Reset buffer
				  MY_UART1.text_index = 0;
				  memset(MY_UART1.text_buffer, 0, sizeof(MY_UART1.text_buffer));
			  }
		  }
	  }
	  
	  // Blink LED
	  static uint32_t last_blink = 0;
	  if(HAL_GetTick() - last_blink > 500){
		  HAL_GPIO_TogglePin(LED_BLINK_GPIO_Port, LED_BLINK_Pin);
		  last_blink = HAL_GetTick();
	  }
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief I2C1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C1_Init(void)
{

  /* USER CODE BEGIN I2C1_Init 0 */

  /* USER CODE END I2C1_Init 0 */

  /* USER CODE BEGIN I2C1_Init 1 */

  /* USER CODE END I2C1_Init 1 */
  hi2c1.Instance = I2C1;
  hi2c1.Init.ClockSpeed = 400000;
  hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C1_Init 2 */

  /* USER CODE END I2C1_Init 2 */

}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 115200;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * Enable DMA controller clock
  */
static void MX_DMA_Init(void)
{

  /* DMA controller clock enable */
  __HAL_RCC_DMA1_CLK_ENABLE();

  /* DMA interrupt init */
  /* DMA1_Channel5_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(DMA1_Channel5_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Channel5_IRQn);

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOC, LED_BLINK_Pin|EN_SYNC_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, B1_Pin|B2_Pin|B3_Pin|B4_Pin
                          |B5_Pin|B6_Pin|B7_Pin|B8_Pin
                          |B9_Pin|B10_Pin|B11_Pin|B12_Pin
                          |B13_Pin|B16_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOB, B14_Pin|B15_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pins : LED_BLINK_Pin EN_SYNC_Pin */
  GPIO_InitStruct.Pin = LED_BLINK_Pin|EN_SYNC_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pins : B1_Pin B2_Pin B3_Pin B4_Pin
                           B5_Pin B6_Pin B7_Pin B8_Pin
                           B9_Pin B10_Pin B11_Pin B12_Pin
                           B13_Pin B16_Pin */
  GPIO_InitStruct.Pin = B1_Pin|B2_Pin|B3_Pin|B4_Pin
                          |B5_Pin|B6_Pin|B7_Pin|B8_Pin
                          |B9_Pin|B10_Pin|B11_Pin|B12_Pin
                          |B13_Pin|B16_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pins : B14_Pin B15_Pin */
  GPIO_InitStruct.Pin = B14_Pin|B15_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /*Configure GPIO pins : PB_UP_Pin PB_DOWN_Pin */
  GPIO_InitStruct.Pin = PB_UP_Pin|PB_DOWN_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

}

/* USER CODE BEGIN 4 */
void GPIO_Init(void){
	GPIO_InitTypeDef GPIO_InitStruct = {0};
	GPIO_InitStruct.Pin = B13_Pin | B14_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart){
	if(huart->Instance == USART1){
		// Cari newline character dalam buffer
		for(uint8_t i = 0; i < len_uart1; i++){
			if(MY_UART1.UART_RX[i] == '\n' || MY_UART1.UART_RX[i] == '\r'){
				// Null-terminate sebelum newline
				MY_UART1.UART_RX[i] = '\0';
				
				// Konversi string ke integer
				int value = atoi((char*)MY_UART1.UART_RX);
				
				// Validasi range 0-360
				if(value < 0) value = 0;
				if(value > 360) value = 360;
				
				// Update nilai
				digital_val = (uint16_t)value;
				syncro_val = (float)value;
				
				// Set flag untuk update GPIO
				HAL_GPIO_WritePin(EN_SYNC_GPIO_Port, EN_SYNC_Pin, SET);
				
				// Clear buffer
				memset(MY_UART1.UART_RX, 0, len_uart1);
				
				// Restart DMA reception
				HAL_UART_Receive_DMA(&huart1, MY_UART1.UART_RX, len_uart1);
				
				break;
			}
		}
	}
}
/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */

  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     tex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
