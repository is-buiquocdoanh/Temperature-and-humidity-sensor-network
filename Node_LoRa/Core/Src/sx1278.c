#include "sx1278.h"

// Register addresses
#define REG_FIFO            0x00
#define REG_OP_MODE         0x01
#define REG_FIFO_ADDR_PTR   0x0D
#define REG_FIFO_RX_CURRENT_ADDR 0x10
#define REG_RX_NB_BYTES     0x13
#define REG_IRQ_FLAGS       0x12
#define REG_DIO_MAPPING1    0x40
#define REG_FRF_MSB         0x06
#define REG_FRF_MID         0x07
#define REG_FRF_LSB         0x08
#define REG_PA_CONFIG       0x09
#define REG_MODEM_CONFIG1   0x1D
#define REG_MODEM_CONFIG2   0x1E
#define REG_MODEM_CONFIG3   0x26
#define REG_PAYLOAD_LENGTH  0x22

#define MODE_LONG_RANGE_MODE   0x80
#define MODE_SLEEP             0x00
#define MODE_STDBY             0x01
#define MODE_TX                0x03
#define MODE_RX_CONTINUOUS     0x05

#define IRQ_RX_DONE_MASK       0x40
#define IRQ_TX_DONE_MASK       0x08

void SX1278_Select(SX1278_t *dev) {
    HAL_GPIO_WritePin(dev->nss_port, dev->nss_pin, GPIO_PIN_RESET);
}

void SX1278_Unselect(SX1278_t *dev) {
    HAL_GPIO_WritePin(dev->nss_port, dev->nss_pin, GPIO_PIN_SET);
}

void SX1278_Reset(SX1278_t *dev) {
    HAL_GPIO_WritePin(dev->reset_port, dev->reset_pin, GPIO_PIN_RESET);
    HAL_Delay(10);
    HAL_GPIO_WritePin(dev->reset_port, dev->reset_pin, GPIO_PIN_SET);
    HAL_Delay(10);
}

uint8_t SX1278_ReadRegister(SX1278_t *dev, uint8_t addr) {
    uint8_t tx[2] = { addr & 0x7F, 0x00 };
    uint8_t rx[2] = {0};
    SX1278_Select(dev);
    HAL_SPI_TransmitReceive(dev->hspi, tx, rx, 2, HAL_MAX_DELAY);
    SX1278_Unselect(dev);
    return rx[1];
}

void SX1278_WriteRegister(SX1278_t *dev, uint8_t addr, uint8_t value) {
    uint8_t tx[2] = { addr | 0x80, value };
    SX1278_Select(dev);
    HAL_SPI_Transmit(dev->hspi, tx, 2, HAL_MAX_DELAY);
    SX1278_Unselect(dev);
}

void SX1278_WriteBurst(SX1278_t *dev, uint8_t addr, uint8_t *data, uint8_t len) {
    SX1278_Select(dev);
    uint8_t cmd = addr | 0x80;
    HAL_SPI_Transmit(dev->hspi, &cmd, 1, HAL_MAX_DELAY);
    HAL_SPI_Transmit(dev->hspi, data, len, HAL_MAX_DELAY);
    SX1278_Unselect(dev);
}

void SX1278_ReadBurst(SX1278_t *dev, uint8_t addr, uint8_t *data, uint8_t len) {
    SX1278_Select(dev);
    uint8_t cmd = addr & 0x7F;
    HAL_SPI_Transmit(dev->hspi, &cmd, 1, HAL_MAX_DELAY);
    HAL_SPI_Receive(dev->hspi, data, len, HAL_MAX_DELAY);
    SX1278_Unselect(dev);
}

bool SX1278_Init(SX1278_t *dev) {
    SX1278_Reset(dev);

    uint8_t version = SX1278_ReadRegister(dev, 0x42);
    if (version != 0x12) return false;

    SX1278_WriteRegister(dev, REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_SLEEP);
    HAL_Delay(10);

    SX1278_WriteRegister(dev, REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_STDBY);

    // Tần số 433 MHz
    SX1278_WriteRegister(dev, REG_FRF_MSB, 0x6C);
    SX1278_WriteRegister(dev, REG_FRF_MID, 0x80);
    SX1278_WriteRegister(dev, REG_FRF_LSB, 0x00);

    // Công suất tối đa + PA_BOOST
    SX1278_WriteRegister(dev, REG_PA_CONFIG, 0x8F);

    // BW = 125kHz, CR = 4/5
    SX1278_WriteRegister(dev, REG_MODEM_CONFIG1, 0x72);

    // SF = 7, CRC ON
    SX1278_WriteRegister(dev, REG_MODEM_CONFIG2, 0x74);

    // AGC ON, LowDataRateOptimize OFF
    SX1278_WriteRegister(dev, REG_MODEM_CONFIG3, 0x04);

    return true;
}

bool SX1278_Transmit(SX1278_t *dev, uint8_t *data, uint8_t len) {
    SX1278_SetStandby(dev);

    SX1278_WriteRegister(dev, REG_IRQ_FLAGS, 0xFF);
    SX1278_WriteRegister(dev, REG_FIFO_ADDR_PTR, 0x00);
    SX1278_WriteBurst(dev, REG_FIFO, data, len);
    SX1278_WriteRegister(dev, REG_PAYLOAD_LENGTH, len);
    SX1278_WriteRegister(dev, REG_DIO_MAPPING1, 0x40); // TxDone

    SX1278_SetTxMode(dev);

    uint32_t start = HAL_GetTick();
    while (!(SX1278_ReadRegister(dev, REG_IRQ_FLAGS) & IRQ_TX_DONE_MASK)) {
        if (HAL_GetTick() - start > 2000) return false;
    }

    SX1278_WriteRegister(dev, REG_IRQ_FLAGS, IRQ_TX_DONE_MASK);
    return true;
}

bool SX1278_Receive(SX1278_t *dev, uint8_t *buffer, uint8_t maxLen) {
    SX1278_SetStandby(dev);

    SX1278_WriteRegister(dev, REG_IRQ_FLAGS, 0xFF); // Clear IRQ flags
    SX1278_WriteRegister(dev, REG_DIO_MAPPING1, 0x00); // DIO0 = RxDone
    SX1278_WriteRegister(dev, REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_RX_CONTINUOUS);

    uint32_t start = HAL_GetTick();
    while (!(SX1278_ReadRegister(dev, REG_IRQ_FLAGS) & IRQ_RX_DONE_MASK)) {
        if (HAL_GetTick() - start > 3000) {
            return false;  // Timeout
        }
    }

    uint8_t len = SX1278_ReadRegister(dev, REG_RX_NB_BYTES);
    if (len == 0 || len >= maxLen) return false;  // Không có data hoặc quá dài

    uint8_t fifoAddr = SX1278_ReadRegister(dev, REG_FIFO_RX_CURRENT_ADDR);
    SX1278_WriteRegister(dev, REG_FIFO_ADDR_PTR, fifoAddr);

    SX1278_ReadBurst(dev, REG_FIFO, buffer, len);
    buffer[len] = '\0';

    SX1278_WriteRegister(dev, REG_IRQ_FLAGS, 0xFF); // Clear flags
    return true;
}


void SX1278_SetStandby(SX1278_t *dev) {
    SX1278_WriteRegister(dev, REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_STDBY);
}

void SX1278_SetTxMode(SX1278_t *dev) {
    SX1278_WriteRegister(dev, REG_OP_MODE, MODE_LONG_RANGE_MODE | MODE_TX);
}
