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

// DSC Helper Defines (dari ROME_DSC1)
#define DSC_MASK_PA   0x1FFF    // PA0–PA12
#define DSC_BIT13_PB  (1 << 10) // PB10
#define DSC_BIT14_PB  (1 << 11) // PB11
#define DSC_BIT15_PA  (1 << 15) // PA15

#define DSC_EN_PORT GPIOC
#define DSC_EN_PIN  GPIO_PIN_14
#define RX_BUF_SIZE 16
#define DSC_ZERO_OFFSET 0xAAAB

// UART Variables
uint8_t rx_byte;
uint8_t rx_buffer[RX_BUF_SIZE];
uint8_t rx_index = 0;
volatile uint8_t rx_ready = 0;
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

// DSC Helper Functions (dari ROME_DSC1)
void DSC_SetData(uint16_t value);
void DSC_Update(uint16_t pos);
uint16_t DSC_ApplyOffset(uint16_t raw_dsc);
uint16_t DSC_LogicalToRaw(uint16_t logical);
uint16_t DSC_ReverseLogical(uint16_t logical);
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
  
  // EN_SYNC init with pull-up (prevents floating when not driven)
  HAL_GPIO_WritePin(EN_SYNC_GPIO_Port, EN_SYNC_Pin, GPIO_PIN_RESET);
  
  // LED OFF by default (Active LOW: SET=OFF)
  HAL_GPIO_WritePin(LED_BLINK_GPIO_Port, LED_BLINK_Pin, GPIO_PIN_SET);
  
  // Kirim pesan awal via UART
  sprintf(txt, "Device #%d Ready\r\n", DEVICE_ID);
  HAL_UART_Transmit(&huart1, (uint8_t*)txt, strlen(txt), 100);
  
  // Start UART interrupt reception (dari ROME_DSC1)
  HAL_UART_Receive_IT(&huart1, &rx_byte, 1);
  
  // Init motor position
  DSC_Update(DSC_ZERO_OFFSET);
  HAL_Delay(100);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  
  while (1)
  {
    // Check if data ready (set by interrupt callback)
    if(rx_ready){
      uint16_t raw_data;
      
      // Parse 3-byte packet: [ID, MSB, LSB]
      raw_data = ((uint16_t)rx_buffer[1] << 8) | rx_buffer[2];
      digital_val = raw_data;
      
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

      // Update Output GPIO - Pakai DSC helper functions
      uint16_t logical_rev = DSC_ReverseLogical(digital_val);
      uint16_t raw_to_dsc = DSC_LogicalToRaw(logical_rev);
      DSC_Update(raw_to_dsc);

      // Toggle LED (non-blocking) - Active LOW
      HAL_GPIO_TogglePin(LED_BLINK_GPIO_Port, LED_BLINK_Pin);
      
      // Reset flags
      rx_index = 0;
      rx_ready = 0;
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
  GPIO_InitStruct.Pull = GPIO_PULLUP;  // Pull-up untuk EN_SYNC agar tidak floating
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  GPIO_InitStruct.Pin = B1_Pin|B2_Pin|B3_Pin|B4_Pin
                          |B5_Pin|B6_Pin|B7_Pin|B8_Pin
                          |B9_Pin|B10_Pin|B11_Pin|B12_Pin
                          |B13_Pin|B16_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_PULLDOWN;  // Pull-down agar default = 0 saat floating
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  GPIO_InitStruct.Pin = B14_Pin|B15_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_PULLDOWN;  // Pull-down agar default = 0 saat floating
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  GPIO_InitStruct.Pin = PB_UP_Pin|PB_DOWN_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
}

/* USER CODE BEGIN 4 */

// UART Interrupt Callback (dari ROME_DSC1)
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
  if (huart->Instance == USART1)
  {
    if(!rx_ready){
      if(rx_index < 3){
        rx_buffer[rx_index++] = rx_byte;
        if(rx_index == 3 && rx_buffer[0] == DEVICE_ID){
          rx_ready = 1;
        }
        else if(rx_index == 3 && rx_buffer[0] != DEVICE_ID){
          rx_index = 0;  // Reset kalau bukan untuk device ini
        }
      }
    }
    // Re-enable interrupt untuk byte berikutnya
    HAL_UART_Receive_IT(&huart1, &rx_byte, 1);
  }
}

// DSC Helper Functions (dari ROME_DSC1)
void DSC_SetData(uint16_t value)
{
    uint32_t bsrr_a = 0;
    uint32_t bsrr_b = 0;

    /* ========= PORT A ========= */
    // PA0–PA12 → Bit 0–12
    bsrr_a |= ((~value & DSC_MASK_PA) << 16); // reset
    bsrr_a |=  ( value & DSC_MASK_PA);        // set

    // PA15 → Bit 15
    if (value & (1 << 15))
        bsrr_a |= DSC_BIT15_PA;
    else
        bsrr_a |= (DSC_BIT15_PA << 16);

    /* ========= PORT B ========= */
    // PB10 → Bit 13
    if (value & (1 << 13))
        bsrr_b |= DSC_BIT13_PB;
    else
        bsrr_b |= (DSC_BIT13_PB << 16);

    // PB11 → Bit 14
    if (value & (1 << 14))
        bsrr_b |= DSC_BIT14_PB;
    else
        bsrr_b |= (DSC_BIT14_PB << 16);

    /* ========= APPLY ========= */
    GPIOA->BSRR = bsrr_a;
    GPIOB->BSRR = bsrr_b;
}

void DSC_Update(uint16_t pos)
{
    DSC_SetData(pos);

    // Pulse EN/LATCH
    HAL_GPIO_WritePin(DSC_EN_PORT, DSC_EN_PIN, GPIO_PIN_RESET);
    __NOP(); __NOP();
    HAL_GPIO_WritePin(DSC_EN_PORT, DSC_EN_PIN, GPIO_PIN_SET);
}

uint16_t DSC_ApplyOffset(uint16_t raw_dsc)
{
    return (uint16_t)(raw_dsc - DSC_ZERO_OFFSET);
}

uint16_t DSC_LogicalToRaw(uint16_t logical)
{
    return (uint16_t)(logical + DSC_ZERO_OFFSET) & 0xFFFF;
}

uint16_t DSC_ReverseLogical(uint16_t logical)
{
    return (uint16_t)(0x10000 - logical);
}

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
