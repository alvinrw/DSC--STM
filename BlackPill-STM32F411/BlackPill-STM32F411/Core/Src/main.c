/* USER CODE BEGIN Header */
/**
  * Master Firmware for STM32F411CEU6 (Black Pill)
  * Protocol: 
  * - RX (UART1 PA10): 15-byte from Raspi
  * - TX (UART2 PA2): 4-byte to Devices [0xBB, ID, MSB, LSB]
  */
/* USER CODE END Header */
#include "main.h"

/* Private variables */
UART_HandleTypeDef huart1;
UART_HandleTypeDef huart2;

// Protocol Definitions
#define PROTOCOL_HEADER_1  0xA5
#define PROTOCOL_HEADER_2  0x99
#define SERIAL_DIST_MARKER 0xBB

// Buffers
uint8_t rx_buffer[15];
uint8_t rx_index = 0;
uint32_t packets_received = 0;
uint32_t packets_distributed = 0;

/* Function Prototypes */
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_USART1_UART_Init(void);
static void MX_USART2_UART_Init(void);

int main(void)
{
  HAL_Init();
  SystemClock_Config();

  MX_GPIO_Init();
  MX_USART1_UART_Init();
  MX_USART2_UART_Init();

  // Blink tanda nyala (PC13 Active Low)
  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET); // LED ON
  HAL_Delay(500);
  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);   // LED OFF

  while (1)
  {
    uint8_t received_byte;
    // Cek data dari Raspi (UART1)
    if(HAL_UART_Receive(&huart1, &received_byte, 1, 10) == HAL_OK){
      
      // 1. Header 1 (0xA5)
      if(rx_index == 0 && received_byte == PROTOCOL_HEADER_1){
        rx_buffer[rx_index++] = received_byte;
      }
      // 2. Header 2 (0x99)
      else if(rx_index == 1){
        if(received_byte == PROTOCOL_HEADER_2){
          rx_buffer[rx_index++] = received_byte;
        } else { rx_index = 0; }
      }
      // 3. Sisa Data body
      else if(rx_index > 1 && rx_index < 15){
        rx_buffer[rx_index++] = received_byte;
        
        // PAKET LENGKAP (15 BYTES)
        if(rx_index == 15){
          packets_received++;
          
          /* --- Distribusi ke 5 Device via UART2 --- */
          for(int dev = 0; dev < 5; dev++){
            uint8_t data_index = 5 + (dev * 2);
            uint8_t msb = rx_buffer[data_index];
            uint8_t lsb = rx_buffer[data_index + 1];
            
            // Paket 4-Byte: [0xBB, ID, MSB, LSB]
            uint8_t serial_packet[4] = {SERIAL_DIST_MARKER, (uint8_t)(dev + 1), msb, lsb};
            
            // Kirim ke Bus (UART2)
            HAL_UART_Transmit(&huart2, serial_packet, 4, 10);
            packets_distributed++;
          }
          
          // Blink LED PC13 (Active Low) - Singkat tanda data masuk
          HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
          HAL_Delay(10);
          HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);
          
          rx_index = 0;
        }
      }
      else { rx_index = 0; }
    }
  }
}

void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 25; // 25MHz xtal
  RCC_OscInitStruct.PLL.PLLN = 192;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 4;
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

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_3) != HAL_OK)
  {
    Error_Handler();
  }
}

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

static void MX_USART2_UART_Init(void)
{
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 115200;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
}

static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);

  /*Configure GPIO pin : PC13 */
  GPIO_InitStruct.Pin = GPIO_PIN_13;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
}

void Error_Handler(void)
{
  __disable_irq();
  while (1) { }
}
