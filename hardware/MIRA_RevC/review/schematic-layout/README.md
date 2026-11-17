# MIRA RevC — схемы для чтения по сигналу

KiCad **10.0.5**, 17 ноября 2026. Исходный `main`: `56f9a9507ec219c7f7b0caf28189b47882f63a45`. Использованы текущие схемы репозитория; архив CH48 не использовался как источник схемотехники.

## Начать просмотр

| Проект | PDF | Страниц до → после | С чего начать |
|---|---|---:|---|
| Control | [Полная схема](PDF/MIRA_Control.pdf) | 62 → 58 | **2600** CH0–CH3; 2100 преобразователи; 3900 маска и защита; 1500 Boot/POR; 1900 USB |
| Power | [Полная схема](PDF/MIRA_Power.pdf) | 57 → 53 | **300** входной путь; **1100** Cincon; 1400 вспомогательные FPGA; 1500 DDR |
| Crossbar | [Полная схема](PDF/MIRA_Crossbar.pdf) | 1 → 1 | **100**, CASE/GND_REF у сокета |

[CH0 — сравнение рядом](CH0/comparison.html) · [Пояснения и отдельные кадры](CH0/README.md) · [Полный тракт CH0 после](CH0/after-full.png).

Номера — настоящие номера страниц KiCad: 100, 200, 300… отдельно в каждом проекте. Они проверены в иерархии и в основных надписях PDF. Номер 2600 соответствует 26-й странице PDF Control.

## Что изменено

- Драйвер и измерение квартета уже были объединены до этой задачи. Теперь **все 12 квартетов CH0–CH47 перерисованы внутри листов**: два ряда по два канала, единое направление сигналов слева направо, общие секции питания и буфер опоры внизу. Большой лист сохраняет полный тракт каждого канала; сокращение формата не делалось ценой уменьшения текста.
- Четырёхканальные OPA4192, OPA4323, MAX313 и TMUX6112 разделены на сигнальные секции и одну общую секцию питания. TLV3202 имеет две секции сравнения и питание. Пины каждого физического корпуса представлены ровно один раз; обозначение и footprint у всех его секций едины. Новые символы находятся в проектной `libraries/MIRA_Readable.kicad_sym`.
- У CH0 видны R260001 5 Ω, два непересекающихся измерительных отвода и INA821 U260013. **R260029 2,60 кОм непосредственно соединён с выводами 2 и 3.** IN+ (4) подключён к стороне драйвера, IN− (1) — к стороне выходного ключа. Положительный ток к электроду увеличивает результат относительно MID2V048. Физическая распиновка не менялась.
- Местная обратная связь 100 кОм / 220 пФ и удалённая ветвь через TMUX6112 и 1 кОм нарисованы проводами. Ветвь напряжения содержит оба буфера, общую точку трёх резисторов масштабирования/подмешивания опоры и RC 47 Ω / 330 пФ. Аналогичный RC показан в токовом тракте. Выходы подписаны конкретными выводами ADC. Разряд и переход к FORMING подписаны у электрода.
- Конфигурация и фильтрация опоры DAC/ADC стоят у соответствующих портов. Регистры масок/аварий имеют видимую развязку, а семь AND-секций каждого из шести банков соединены в дерево от восьми `CH_OK_LATCH` до `BANK_OK`. IEC-маркеры AND/OR и инверсия SN74LVC14A отражают функцию существующих микросхем.
- В Boot/POR собраны подтяжки, CT, делитель порога и цепь разрешения Reset. Для DDR и FX20 развязка собрана общими проводниками по действительным доменам питания; принадлежность конденсаторов отдельным BGA-шарам не выдумывалась. Тридцать конденсаторов питания FX20 перенесены с USB-C на его лист (новые C180026–C180055).
- На USB-C собраны CC/shield, защита и разделительные конденсаторы, VBUS-детектор, кварц с нагрузочными конденсаторами и RC Reset. Ручные участки STM32, разделение банков Zynq и интерфейс DDR сохранены там, где они помогают чтению.
- Power: входные ступени соединены в один путь; сохранены уже нарисованные вручную ядра преобразователей. У Cincon видимыми проводами соединены входной/выходной bypass, шунт, ограничительный диод и управление REMOTE. На 20 цепях FB/SW/bootstrap парные метки заменены видимыми проводами ([перечень](power-visible-connections.json)). Длинные панели заменены компактными условиями у схемы; полное содержание сохранено в [Power design notes](power-design-notes.md).
- Crossbar: R10001 CASE и R10002 GND_REF стоят у выводов 40 и 48 U10001 и соединены с землёй. Пробный J10003 с NC-контактами сохранён отдельно от действующей карты CH в U10001; его механику и PCB не меняли.

## Дополнительные объединения

| Проект | Результат | Исходные листы |
|---|---|---|
| Control | **4800 Logic Power and Spare Gates** | C_LogicPower0, C_SpareLogic0, C_LogicPower1 (только заметка), C_LogicPower2, C_SpareLogic1 |
| Power | **1400 FPGA Auxiliary Rails** | FPGA AUX 1.8 V, AUX 2.5 V, FPGA IO 3.3 V |
| Power | **1500 DDR Supply and Termination** | DDR 1.35 V + VTT/reference |
| Power | **1700 Analog LDO Rails** | Analog 5 V + Analog 3.3 V |

Сложные самостоятельные преобразователи, банки FPGA, интерфейс DDR и формирующие коммутаторы остаются отдельными функциональными блоками. [Исходные навигационные заметки](navigation-notes.md) и [заметки переработанных листов Control](control-design-notes.md) сохранены в документации.

## Электрическая проверка и сохранность PCB

Все три ERC: **0 нарушений до и после**, с прежними правилами и исключениями. Экспорт/повторное чтение выполнены установленным KiCad 10.0.5. Использовался его нативный CLI из AppImage; интерактивная GUI-проверка не выдаётся за выполненную.

Проверено сохранение эффективных классов сетей, включая USB differential pairs. Сравнены полные группы `(обозначение, номер вывода)` каждой сети, состав компонентов, номиналы, MPN, производитель, datasheet, footprints, DNP/исключения и физические определения выводов. Проверены и разрывы, и случайные слияния. Полезные имена сетей сохранены: внутренние локальные метки могут получить иерархический префикс, внешние переходы остаются глобальными. `verify_ch48.py` нормализует только однозначные локальные имена CH0–CH47 и **отклоняет неоднозначное совпадение**, не объединяя независимые сети.

| Проект | Компонентов до = после | Выводов в netlist | Сетей до = после |
|---|---:|---:|---:|
| Control | 2189 | 9266 | 2191 |
| Power | 793 | 2571 | 446 |
| Crossbar | 6 | 300 | 197 |

`verify_ch48.py`: **PASS** — 48 электродных цепей, 96 ADC inputs, 48 DAC outputs, 144 forming taps, 48 bleed controls, 168 позиций ответных разъёмов и 64 вывода сокета.

Сохранены все исходные UUID экземпляров схемы. Добавлены только секции уже существовавших корпусов. Геометрия всех **3136 footprints PCB**, площадки, координаты, стороны, повороты, сети, трассы, контуры и привязанные 3D-модели сохранены. Изменения PCB ограничены обозначениями и необходимыми путями к перенесённым символам; точный перечень — [pcb-binding-changes.csv](pcb-binding-changes.csv). Настройки `.kicad_pro` и механические наработки пользователя сохранены; посторонние локальные изменения остаются вне коммита задачи.

- [validation.json](validation.json): итог проверок и версия KiCad.
- [erc](erc): актуальные JSON и текстовые ERC.
- [netlists](netlists): итоговые XML, сжатые gzip.
- [readability-reference-map.json](readability-reference-map.json): обозначения перед этой задачей → текущие.
- [reference-map.json](reference-map.json): исходные обозначения CH48-контракта → текущие, включая прежние миграции.
- [readability-baseline](readability-baseline): сохранённые исходные PDF, свежие исходные netlists/ERC, состояние Git и PCB bindings. Полный локальный снимок рабочих проектов: `/tmp/mira-readable/original`. Схемы и платы исходного состояния доступны также в исходном коммите; локальные настройки сохранены в рабочей копии.

Схемотехника не изменялась. Подтверждённой новой электрической ошибки при перерисовке не выявлено. Существующее состояние PCB и пробного сокета сохранено для отдельной последующей работы над платами.

## Повторить проверки

Из `hardware/MIRA_RevC`, с `kicad-cli` версии 10.0.5:

```sh
kicad-cli sch erc --exit-code-violations -o /tmp/control-erc.rpt MIRA_Control/MIRA_Control.kicad_sch
kicad-cli sch export netlist --format kicadxml -o /tmp/control.xml MIRA_Control/MIRA_Control.kicad_sch
python3 review/schematic-layout/compare_netlists.py MIRA_Control review/schematic-layout/readability-baseline/netlists/MIRA_Control.xml.gz /tmp/control.xml --reference-map review/schematic-layout/readability-reference-map.json
kicad-cli sch export netlist --format kicadxml -o /tmp/crossbar.xml MIRA_Crossbar/MIRA_Crossbar.kicad_sch
python3 review/ch48/verify_ch48.py /tmp/control.xml /tmp/crossbar.xml --reference-map review/schematic-layout/reference-map.json
python3 review/schematic-layout/audit_layout.py --baseline /tmp/mira-readable/original
```

Аналогично экспортируются и сравниваются Power и Crossbar. `compare_netlists.py` сопоставляет физические выводы конкретного компонента, поэтому корректное разделение символа на секции не считается сменой микросхемы. `audit_layout.py` дополнительно проверяет номера страниц, UUID, состав новых многосекционных корпусов и доказательство сохранности PCB. Для другого исходного снимка выбирайте соответствующую карту обозначений.

## Полный перечень страниц

### MIRA_Control

| Страница | Название | Файл |
|---:|---|---|
| 100 | Control Overview | `MIRA_Control.kicad_sch` |
| 200 | MCU | `MCU.kicad_sch` |
| 300 | MCU Power and Debug | `100_MCU_POWER_CLOCKS_AND_DEBUG.kicad_sch` |
| 400 | MCU SDRAM | `200_MCU_FMC_AND_SDRAM.kicad_sch` |
| 500 | MCU Storage and Control | `300_MCU_QSPI_MICROSD_AND_CONTROL.kicad_sch` |
| 600 | Power Interface | `INTERCONNECT.kicad_sch` |
| 700 | Supervisor Interface | `400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch` |
| 800 | Digital Power Entry | `410_DISTRIBUTED_DIGITAL_POWER.kicad_sch` |
| 900 | Analog Power Entry | `420_DISTRIBUTED_ANALOG_POWER.kicad_sch` |
| 1000 | Zynq and Memory | `C_GROUP_ZYNQ.kicad_sch` |
| 1100 | Zynq PL I-O | `C_SOC0.kicad_sch` |
| 1200 | Zynq PS I-O | `C_SOC1.kicad_sch` |
| 1300 | Zynq Config and Power | `C_SOC2.kicad_sch` |
| 1400 | Zynq DDR3L | `C_DDR.kicad_sch` |
| 1500 | Zynq Boot and Reset | `C_Boot.kicad_sch` |
| 1600 | Zynq Decoupling | `C_Decoupling.kicad_sch` |
| 1700 | USB Interface | `C_GROUP_USB.kicad_sch` |
| 1800 | FX20 Bridge | `C_FX20.kicad_sch` |
| 1900 | USB-C Port | `C_USB_C.kicad_sch` |
| 2000 | DAC and ADC Banks | `C_GROUP_CONVERTERS.kicad_sch` |
| 2100 | CH00-15 Converters | `C_Bank0.kicad_sch` |
| 2200 | CH16-31 Converters | `C_Bank1.kicad_sch` |
| 2300 | CH32-47 Converters | `C_Bank2.kicad_sch` |
| 2400 | CH48 Analog Channels | `C_GROUP_LINES.kicad_sch` |
| 2500 | Channel Signal Flow | `C_ChannelGuide.kicad_sch` |
| 2600 | CH00-03 Drive and Sense | `C_AFE_BL0_BL3.kicad_sch` |
| 2700 | CH04-07 Drive and Sense | `C_AFE_BL4_BL7.kicad_sch` |
| 2800 | CH08-11 Drive and Sense | `C_AFE_BL8_BL11.kicad_sch` |
| 2900 | CH12-15 Drive and Sense | `C_AFE_BL12_BL15.kicad_sch` |
| 3000 | CH16-19 Drive and Sense | `C_AFE_BL16_BL19.kicad_sch` |
| 3100 | CH20-23 Drive and Sense | `C_AFE_BL20_BL23.kicad_sch` |
| 3200 | CH24-27 Drive and Sense | `C_AFE_BL24_BL27.kicad_sch` |
| 3300 | CH28-31 Drive and Sense | `C_AFE_BL28_BL31.kicad_sch` |
| 3400 | CH32-35 Drive and Sense | `C_AFE_NL0_NL3.kicad_sch` |
| 3500 | CH36-39 Drive and Sense | `C_AFE_NL4_NL7.kicad_sch` |
| 3600 | CH40-43 Drive and Sense | `C_AFE_NL8_NL11.kicad_sch` |
| 3700 | CH44-47 Drive and Sense | `C_AFE_NL12_NL15.kicad_sch` |
| 3800 | Masks and Protection | `C_GROUP_SAFETY.kicad_sch` |
| 3900 | CH00-07 Mask and Fault | `C_Mask0.kicad_sch` |
| 4000 | CH08-15 Mask and Fault | `C_Mask1.kicad_sch` |
| 4100 | CH16-23 Mask and Fault | `C_Mask2.kicad_sch` |
| 4200 | CH24-31 Mask and Fault | `C_Mask3.kicad_sch` |
| 4300 | CH32-39 Mask and Fault | `C_Mask4.kicad_sch` |
| 4400 | CH40-47 Mask and Fault | `C_Mask5.kicad_sch` |
| 4500 | Global Fault Latch | `C_Global.kicad_sch` |
| 4600 | Service DAC and Servo | `C_Service.kicad_sch` |
| 4700 | Mode Blanking | `C_Mode.kicad_sch` |
| 4800 | Logic Power and Spare Gates | `C_LogicPower0.kicad_sch` |
| 4900 | Forming Address Latch | `C_FormAddress.kicad_sch` |
| 5000 | Forming Routes | `C_GROUP_WORDLINES.kicad_sch` |
| 5100 | Gate Supply | `C_WL12.kicad_sch` |
| 5200 | Forming Interlock | `CH48_Interlock.kicad_sch` |
| 5300 | Forming Source | `CH48_Form_BL.kicad_sch` |
| 5400 | Forming Return | `CH48_Form_NL.kicad_sch` |
| 5500 | Forming Gate | `CH48_Form_WL.kicad_sch` |
| 5600 | Electrode Isolation | `CH48_Form_Isolation.kicad_sch` |
| 5700 | Module Interface | `C_GROUP_MODULE.kicad_sch` |
| 5800 | CH48 Module Connectors | `C_Crossbar.kicad_sch` |

### MIRA_Power

| Страница | Название | Файл |
|---:|---|---|
| 100 | Power Overview | `MIRA_Power.kicad_sch` |
| 200 | Power Distribution | `POWER_SYSTEM.kicad_sch` |
| 300 | 24 V Input and Protection | `POWER_INPUT.kicad_sch` |
| 400 | Primary Converters | `PRIMARY_POWER.kicad_sch` |
| 500 | AON 3.3 V | `500_AON_3V3_BUCK.kicad_sch` |
| 600 | USB 5 V | `600_USB_5V.kicad_sch` |
| 700 | System 3.3 V | `700_SYS_3V3.kicad_sch` |
| 800 | FPGA 5.5 V | `800_FPGA_INTERMEDIATE_5V5.kicad_sch` |
| 900 | Analog 6 V | `900_ANALOG_PREREGULATOR_6V.kicad_sch` |
| 1000 | AFE +15 V | `1000_AFE_POSITIVE_15V.kicad_sch` |
| 1100 | AFE -15 V | `1100_AFE_NEGATIVE_15V.kicad_sch` |
| 1200 | Secondary Converters | `SECONDARY_POWER.kicad_sch` |
| 1300 | FPGA Core 1 V | `1200_POWER_MONITOR.kicad_sch` |
| 1400 | FPGA Auxiliary Rails | `1300_FPGA_AUX_1V8.kicad_sch` |
| 1500 | DDR Supply and Termination | `1600_DDR_1V35.kicad_sch` |
| 1600 | I-O 1.8 V | `1700_IO_1V8.kicad_sch` |
| 1700 | Analog LDO Rails | `1900_ANALOG_5V.kicad_sch` |
| 1800 | Programming Rails | `PROGRAM_SWITCHES.kicad_sch` |
| 1900 | Program Positive | `2100_PROGRAM_POSITIVE.kicad_sch` |
| 2000 | Program Negative | `2200_PROGRAM_NEGATIVE.kicad_sch` |
| 2100 | Program Interface | `2300_PROGRAM_INTERFACE.kicad_sch` |
| 2200 | Control Board Outputs | `4900_POWER_CONTROL_INTERFACE.kicad_sch` |
| 2300 | Digital Power Outputs | `5000_DISTRIBUTED_DIGITAL_POWER.kicad_sch` |
| 2400 | Analog Power Outputs | `5100_DISTRIBUTED_ANALOG_POWER.kicad_sch` |
| 2500 | Power Sequencing | `POWER_CONTROL.kicad_sch` |
| 2600 | Power Manager MCU | `2400_PM_CONTROLLER.kicad_sch` |
| 2700 | Supply Watchdogs | `2500_PM_WATCHDOGS.kicad_sch` |
| 2800 | Host Link Watchdog | `5400_HOST_LINK_WATCHDOG.kicad_sch` |
| 2900 | Host Input Isolation | `5500_AON_HOST_INPUT_ISOLATION.kicad_sch` |
| 3000 | Startup Qualifier | `5200_PM_STARTUP_QUALIFIER.kicad_sch` |
| 3100 | Permit Interlocks | `2600_PM_PERMIT_INTERLOCKS.kicad_sch` |
| 3200 | Primary Enable Gates | `2700_PM_ENABLE_GATES_PRIMARY.kicad_sch` |
| 3300 | Aux Enable Gates | `2800_PM_ENABLE_GATES_AUXILIARY.kicad_sch` |
| 3400 | Startup Output Gates | `5300_PM_STARTUP_OUTPUTS.kicad_sch` |
| 3500 | VIN Enables 1 | `5800_VIN_REFERENCED_ENABLES.kicad_sch` |
| 3600 | VIN Enables 2 | `5900_VIN_REFERENCED_ENABLES.kicad_sch` |
| 3700 | FPGA Aux Interlock | `6000_FPGA_AUX_IO_INTERLOCK.kicad_sch` |
| 3800 | Analog Power Good | `2900_PM_ANALOG_POWER_GOOD.kicad_sch` |
| 3900 | Rail Ready | `3000_PM_RAIL_READY.kicad_sch` |
| 4000 | Command Ready | `3100_PM_COMMAND_READY.kicad_sch` |
| 4100 | Negative Overcurrent | `3200_PM_NEGATIVE_OVERCURRENT.kicad_sch` |
| 4200 | PM Debug and Host | `3300_PM_DEBUG_HOST_INTERFACE.kicad_sch` |
| 4300 | Rail Monitoring | `POWER_MONITOR.kicad_sch` |
| 4400 | Negative Rail Sense | `3400_NEGATIVE_RAIL_MONITOR.kicad_sch` |
| 4500 | Input and System Sense | `3500_MONITOR_INPUT_AON_USB_SYS.kicad_sch` |
| 4600 | Primary Rail Sense | `3600_MONITOR_FPGA_ANA_AFE.kicad_sch` |
| 4700 | FPGA Rail Sense | `3700_MONITOR_FPGA_CORE_AUX_IO.kicad_sch` |
| 4800 | DDR and Analog Sense | `3800_MONITOR_DDR_IO_ANALOG.kicad_sch` |
| 4900 | Analog Isolation 1 | `5600_AON_ANALOG_INPUT_ISOLATION.kicad_sch` |
| 5000 | Analog Isolation 2 | `5700_AON_ANALOG_INPUT_ISOLATION.kicad_sch` |
| 5100 | Monitor Enable Buffer | `6100_AON_MONITOR_ENABLE_BUFFER.kicad_sch` |
| 5200 | Telemetry Selectors | `3900_TELEMETRY_MULTIPLEXERS.kicad_sch` |
| 5300 | Telemetry ADC Buffers | `4000_TELEMETRY_ADC_BUFFERS.kicad_sch` |

### MIRA_Crossbar

| Страница | Название | Файл |
|---:|---|---|
| 100 | CH48 Crossbar | `MIRA_Crossbar.kicad_sch` |
