/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
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
uint16_t digital_val=0;
uint8_t dsc_mode=1;
/* USER CODE END PFP */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */
  char txt[30];
  /* USER CODE END 1 */

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* Configure the system clock */
  SystemClock_Config();

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
  
  // Init OLED
  HAL_Delay(200);
  SSD1306_Init();
  HAL_Delay(100);
  
  SSD1306_GotoXY(10,0);
  sprintf(txt, "Device: #%d", DEVICE_ID);
  SSD1306_Puts(txt, &Font_7x10, 1);
  SSD1306_UpdateScreen();
  HAL_Delay(50);
  
  SSD1306_GotoXY(10,15);
  SSD1306_Puts("Digital: 0   ", &Font_7x10, 1);
  SSD1306_UpdateScreen();
  HAL_Delay(50);
  
  SSD1306_GotoXY(10,35);
  SSD1306_Puts("Syncro: 0.00  ", &Font_7x10, 1);
  SSD1306_UpdateScreen();
  HAL_Delay(50);
  
  SSD1306_GotoXY(5,55);
  SSD1306_Puts("Waiting...", &Font_7x10, 1);
  SSD1306_UpdateScreen();
  HAL_Delay(50);
  
  // Init GPIO output - set all to 0
  dsc(0);
  
  // LED OFF by default (Active LOW: SET=OFF)
  HAL_GPIO_WritePin(LED_BLINK_GPIO_Port, LED_BLINK_Pin, GPIO_PIN_SET);
  
  // Kirim pesan awal via UART
  sprintf(txt, "Device #%d Ready\r\n", DEVICE_ID);
  HAL_UART_Transmit(&huart1, (uint8_t*)txt, strlen(txt), 100);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  
  // Buffer untuk terima 4 bytes distribusi Serial dari Master
  uint8_t serial_rx_buffer[SERIAL_PACKET_SIZE];
  uint8_t serial_rx_index = 0;
  
  while (1)
  {
    // Terima 1 byte dari Master via UART (Shared Bus)
    uint8_t rx_byte;
    if(HAL_UART_Receive(&huart1, &rx_byte, 1, 5) == HAL_OK){
      
      // 1. Cari Start Marker (0xBB)
      if(serial_rx_index == 0 && rx_byte == SERIAL_DIST_MARKER){
        serial_rx_buffer[serial_rx_index++] = rx_byte;
      }
      // 2. Kumpulkan byte berikutnya
      else if(serial_rx_index > 0){
        serial_rx_buffer[serial_rx_index++] = rx_byte;
        
        // 3. Jika paket lengkap (4 byte)
        if(serial_rx_index == SERIAL_PACKET_SIZE){
          uint8_t target_id = serial_rx_buffer[1];
          
          // 4. Filter berdasarkan DEVICE_ID
          if(target_id == DEVICE_ID){
            uint8_t byte_high = serial_rx_buffer[2];
            uint8_t byte_low = serial_rx_buffer[3];

            digital_val = (uint16_t)((byte_high << 8) | byte_low);
            
            // Decoding berdasarkan DEVICE_ID
            if(DEVICE_ID == 5){
              int16_t signed_val = (int16_t)digital_val;
              syncro_val = ((float)signed_val / 10.0f) - 179.9f;
            }
            else{
              syncro_val = (float)digital_val / 10.0f;
            }

            // Update OLED
            SSD1306_GotoXY(10,15);
            sprintf(txt, "Digital: %u   ", digital_val);
            SSD1306_Puts(txt, &Font_7x10, 1);

            SSD1306_GotoXY(10,35);
            sprintf(txt, "Syncro: %.2f  ", syncro_val);
            SSD1306_Puts(txt, &Font_7x10, 1);

            SSD1306_UpdateScreen();

            // Update Output GPIO
            dsc(digital_val);

            // Blink LED (Active LOW: RESET=ON, SET=OFF)
            HAL_GPIO_WritePin(LED_BLINK_GPIO_Port, LED_BLINK_Pin, GPIO_PIN_RESET); // Nyala
            HAL_Delay(50);
            HAL_GPIO_WritePin(LED_BLINK_GPIO_Port, LED_BLINK_Pin, GPIO_PIN_SET);   // Mati
          }
          
          // Reset buffer untuk paket berikutnya
          serial_rx_index = 0;
        }
      }
    }

    // LED stays ON (no heartbeat blink)
    // LED will blink only when broadcast data is received
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
  */
static void MX_I2C1_Init(void)
{
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
}

/**
  * @brief USART1 Initialization Function
  */
static void MX_USART1_UART_Init(void)
{
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
}

/**
  * Enable DMA controller clock
  */
static void MX_DMA_Init(void)
{
  __HAL_RCC_DMA1_CLK_ENABLE();
  HAL_NVIC_SetPriority(DMA1_Channel5_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(DMA1_Channel5_IRQn);
}

/**
  * @brief GPIO Initialization Function
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  HAL_GPIO_WritePin(GPIOC, LED_BLINK_Pin|EN_SYNC_Pin, GPIO_PIN_RESET);

  HAL_GPIO_WritePin(GPIOA, B1_Pin|B2_Pin|B3_Pin|B4_Pin
                          |B5_Pin|B6_Pin|B7_Pin|B8_Pin
                          |B9_Pin|B10_Pin|B11_Pin|B12_Pin
                          |B13_Pin|B16_Pin, GPIO_PIN_RESET);

  HAL_GPIO_WritePin(GPIOB, B14_Pin|B15_Pin, GPIO_PIN_RESET);

  GPIO_InitStruct.Pin = LED_BLINK_Pin|EN_SYNC_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  GPIO_InitStruct.Pin = B1_Pin|B2_Pin|B3_Pin|B4_Pin
                          |B5_Pin|B6_Pin|B7_Pin|B8_Pin
                          |B9_Pin|B10_Pin|B11_Pin|B12_Pin
                          |B13_Pin|B16_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  GPIO_InitStruct.Pin = B14_Pin|B15_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  GPIO_InitStruct.Pin = PB_UP_Pin|PB_DOWN_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  */
void Error_Handler(void)
{
  __disable_irq();
  while (1)
  {
  }
}

#ifdef  USE_FULL_ASSERT
void assert_failed(uint8_t *file, uint32_t line)
{
}
#endif
