# MSeq PCB

[![KiCad ERC / DRC](https://github.com/MF-Room/mseq_pcb/actions/workflows/kicad-checks.yml/badge.svg)](https://github.com/MF-Room/mseq_pcb/actions/workflows/kicad-checks.yml)

KiCad 10 hardware design for [MSeq embedded](https://github.com/MF-Room/mseq_embedded),
the microcontroller implementation of the [MSeq](https://github.com/MF-Room/mseq) MIDI sequencer.

## Main specs
* MCU: STM32F413CHU6 (Arm Cortex-M4F, 100 MHz), 25 MHz HSE and 32.768 kHz LSE crystals
* MIDI: 2 × IN (H11L1M opto-isolated), 1 × OUT and 1 × THRU (74HCT125 buffered), 5-pin DIN sockets
* USB-C: USB-to-UART bridge (CP2102N) with ESD protection, also powers the board
* Storage: 16 Mbit SPI NOR flash (W25Q16JV) and 256 kbit SPI FRAM (MB85RS256B)
* Power: 5 V from USB, AMS1117-3.3 regulator, ON/OFF switch
* Controls: MASTER/SLAVE sync switch, RESET and BOOT buttons
* Headers: 10-pin SWD/JTAG (1.27 mm), 4-pin I2C header for a display
* LEDs: power, MIDI activity, USB TX/RX
* Board: 2 layers, 135.3 × 78.4 mm, 1.6 mm FR-4, all parts on the top side, made for JLCPCB assembly

## Related repositories
* [mseq_pcb_tb](https://github.com/MF-Room/mseq_pcb_tb) — test bench for the MSeq PCB
* [mseq_embedded](https://github.com/MF-Room/mseq_embedded) — microcontroller implementation of MSeq
* [mseq](https://github.com/MF-Room/mseq) — lightweight MIDI sequencer framework written in Rust

## License
Copyright © 2026 MF Room.

This hardware design is licensed under the CERN Open Hardware Licence Version 2 – Strongly Reciprocal
(SPDX-License-Identifier: `CERN-OHL-S-2.0`). See [LICENSE](LICENSE) for the full text.

Source location: https://github.com/MF-Room/mseq_pcb
