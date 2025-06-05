#ifndef __SX1278_H
#define __SX1278_H

#include "main.h"
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// SX1278 config
#define SX1278_FREQUENCY 433000000  // 433 MHz

typedef struct {
    SPI_HandleTypeDef *hspi;
    GPIO_TypeDef *nss_port;
    uint16_t nss_pin;
    GPIO_TypeDef *reset_port;
    uint16_t reset_pin;
} SX1278_t;

bool SX1278_Init(SX1278_t *dev);
void SX1278_Reset(SX1278_t *dev);
uint8_t SX1278_ReadRegister(SX1278_t *dev, uint8_t addr);
void SX1278_WriteRegister(SX1278_t *dev, uint8_t addr, uint8_t value);
void SX1278_WriteBurst(SX1278_t *dev, uint8_t addr, uint8_t *data, uint8_t len);
void SX1278_ReadBurst(SX1278_t *dev, uint8_t addr, uint8_t *data, uint8_t len);
void SX1278_SetTxMode(SX1278_t *dev);
void SX1278_SetStandby(SX1278_t *dev);
bool SX1278_Transmit(SX1278_t *dev, uint8_t *data, uint8_t len);
bool SX1278_Receive(SX1278_t *dev, uint8_t *buffer, uint8_t maxLen);


#endif
