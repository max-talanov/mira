# Источники MIRA.04

Данные проверены 30.10.2026. Хеши загруженных оригиналов — в `manifest.json`. Полные сторонние PDF не включены в архив; сохранены ссылки, AMD CSV, ST XML и компактные проверяемые извлечения. Память сверена по документам производителей, размещённым на зеркалах; это явно указано ниже.

- [AMD package pinout](https://download.amd.com/adaptive-socs-and-fpgas/developer/adaptive-socs-and-fpgas/package-pinout-files/a7packages/a7all.zip) — Official a7packages archive; xc7a200tfbg484pkg.csv, 484 pins
- [AMD DS181](https://docs.amd.com/api/khub/documents/iAkxxTOk96ANLJqYf2hgrQ/content) — v1.27.1, 2024-07-03, table 16, p.15; DDR3L PHY limits
- [AMD UG586](https://docs.amd.com/r/en-US/ug586_7Series_MIS/Bank-and-Pin-Selection-Guides-for-DDR3-Designs) — 4.2, 2024-11-13; Bank and Pin Selection Guides for DDR3 Designs
- [AMD UG586 clock](https://docs.amd.com/r/en-US/ug586_7Series_MIS/Input-Clock-Guidelines?contentId=xMPtdYx6gKP_fGhjWtP25A) — 4.2; LVDS input and nonstandard VCCO with external termination
- [AMD UG586 CS](https://docs.amd.com/r/en-US/ug586_7Series_MIS/Traffic-Test-Flow?contentId=cOcO~NNCmX5jDoptwxKXOA) — 4.2; Traffic Test Flow, chip select disable requires memory CS tied low
- [ST DS12923](https://www.st.com/resource/en/datasheet/stm32h745xi.pdf) — Rev 3; STM32H745xI/G pinouts and alternate functions
- [ST MCU XML](https://github.com/STMicroelectronics/STM32_open_pin_data/blob/master/mcu/STM32H745IITx.xml) — Official STM32_open_pin_data; exact LQFP176 device
- [ST GPIO XML](https://github.com/STMicroelectronics/STM32_open_pin_data/blob/master/mcu/IP/GPIO-STM32H747_gpio_v1_0_Modes.xml) — Official shared H745/H747 GPIO IP mapping
- [ST RM0399](https://www.st.com/resource/en/reference_manual/dm00176879-stm32h745-755-and-stm32h747-757-advanced-arm-based-32-bit-mcus-stmicroelectronics.pdf) — Rev 4; SDRAM bank mapping and FMC_SDRTR refresh counter, p.920
- [Micron 4Gb DDR3L](https://datasheet.datasheetarchive.com/originals/dk/DKDS42/DSANUWW0045409.pdf) — Manufacturer PDF Rev R, 09/18; Figure 7 p.18 x16 ball map; Table 56 CL/CWL. Retrieved from a mirror.
- [ISSI IS42/45R/S86400F,16320F](https://www.zlgmcu.com/data/upload/file/powernfc/42-45R-S_86400F-16320F.pdf) — Manufacturer PDF Rev B1, 2017-07-17; TSOP54 pinout and SDRAM organization. Retrieved from a mirror.
- [SiTime SiT9121](https://www.sitime.com/datasheet/SiT9121) — Rev 1.08, 2019-08-17; differential oscillator output
- [AMD UG835](https://docs.amd.com/r/en-US/ug835-vivado-tcl-commands/open_io_design) — 2026.1; create_project, open_io_design, create_port; Tcl preparation only

`mt41k256m16tw-vendor-pins.csv` и `is42s16320f-tsop54-vendor-pins.csv` вручную транскрибированы из таблиц/рисунков производителей. Они независимы от проверяемой KiCad netlist. ST GPIO IP имеет имя H747 по ссылке внутри файла H745; это корректное общее описание IP, не подмена выбранного MCU.

Устаревший PDF UG586 2012 года и пример MIG чужой платы не являются источниками итоговой распиновки. Файлы `.prj` от другой платы не поставляются.
