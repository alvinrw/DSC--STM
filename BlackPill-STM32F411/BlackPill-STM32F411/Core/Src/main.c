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

// Discrete data parsing (dari USART_masudin)
uint8_t payload[15];
uint8_t discreate_A[8];
uint8_t discreate_B[8];
uint8_t discreate_C[8];
const char *navigation_source = NULL;
const char *country_code = NULL;

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
          
          // Parse discrete data (LENGKAP - semua bits)
          for(int i=0; i<8; i++){
            discreate_A[i] = (rx_buffer[2] >> i & 0x01);
            discreate_B[i] = (rx_buffer[3] >> i & 0x01);
            discreate_C[i] = (rx_buffer[4] >> i & 0x01);
          }
          
          // ========== DISCRETE A ==========
          uint8_t gs_valid = discreate_A[0];
          uint8_t gyro_monitor = discreate_A[1];
          uint8_t fd_validity_flag = discreate_A[2];
          uint8_t rot_valid_signal = discreate_A[3];
          uint8_t nvis_sel = discreate_A[4];
          uint8_t dh_input = discreate_A[5];
          
          // ========== DISCRETE B ==========
          // Bit 0-1: EFD-5.5 Run Mode
          uint8_t run_mode = (discreate_B[1] << 1) | discreate_B[0];
          const char *run_mode_str = NULL;
          if(run_mode == 0x00) run_mode_str = "EADI";
          else if(run_mode == 0x01) run_mode_str = "EHSI";
          else if(run_mode == 0x02) run_mode_str = "RDU";
          
          // Bit 2-3: Navigation Source
          uint8_t nav_src = (discreate_B[3] << 1) | discreate_B[2];
          if(nav_src == 0x00) navigation_source = "INS";
          else if(nav_src == 0x01) navigation_source = "TAC";
          else if(nav_src == 0x02) navigation_source = "VOR/ILS";
          
          uint8_t auto_test = discreate_B[4];
          uint8_t lat_bar_in_view = discreate_B[5];
          uint8_t ils_freq_tuned = discreate_B[6];
          uint8_t nav_super_flag = discreate_B[7];
          
          // ========== DISCRETE C ==========
          // Bit 0-1: Country Code
          uint8_t country = (discreate_C[1] << 1) | discreate_C[0];
          if(country == 0x00) country_code = "TNI AU";
          else if(country == 0x01) country_code = "Bangladesh";
          
          uint8_t radio_altimeter_mon = discreate_C[2];
          uint8_t rev_mode_enable = discreate_C[3];
          uint8_t inner_marker = discreate_C[4];
          uint8_t outer_marker = discreate_C[5];
          uint8_t middle_marker = discreate_C[6];
          
          /* NOTE: Discrete variables tersedia untuk digunakan:
           * - run_mode_str, navigation_source, country_code (strings)
           * - gs_valid, gyro_monitor, auto_test, markers, dll (uint8_t flags)
           * Uncomment code di atas jika ingin menggunakan discrete data
           */
          
          
          /* --- Distribusi ke 5 Device via UART2 --- */
          for(int dev = 0; dev < 5; dev++){
            uint8_t data_index = 5 + (dev * 2);
            uint8_t msb = rx_buffer[data_index];
            uint8_t lsb = rx_buffer[data_index + 1];
            
            // Paket 3-Byte: [ID, MSB, LSB] - TANPA marker 0xBB
            uint8_t serial_packet[3] = {(uint8_t)(dev + 1), msb, lsb};
            
            // Kirim ke Bus (UART2)
            HAL_UART_Transmit(&huart2, serial_packet, 3, 10);
            packets_distributed++;
            
            // Delay dikurangi untuk performa (1ms cukup)
            HAL_Delay(1);
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
