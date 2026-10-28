# День 1: подготовка исходной версии к PCB

> Текущая версия: [конкретные разъёмы и исправление ERC](connectors-erc/README.md). Обе схемы проходят включённые проверки без ошибок, предупреждений и исключений; два прежних правила оформления остаются отключёнными.

> Актуальные изменения схем и открытые проверки описаны в [кандидате для высокой нагрузки](high-load/README.md). Ниже сохранена исходная сверка; её статусы не описывают новую схему.

> Подготовлен [кандидат исправлений от 28 октября](fixes/README.md). Статусы ниже относятся к исходной сверке; полное закрытие электрических вопросов пока не подтверждено.

**Обновлено 2026-10-27:** оформлены сверка межплатных соединений и разбор предоставленных отчётов ERC.

- [x] Межплатные цепи выписаны, расхождения отмечены.
- [x] Отчёты ERC сохранены, основные причины разобраны.

Сверка охватывает **Control: 30 активных страниц** и **Power: 48 активных страниц**. Найдены **26 обязательных межплатных цепей**: 16 шин питания и опор, 9 сигналов, GND. Межплатные вопросы I01–I08 включают 3 P0 и 5 P1.

В предоставленных отчётах ERC: **Control — 4 ошибки и 118 предупреждений; Power — 11 ошибок и 13 предупреждений**. Все 146 сообщений сгруппированы в E01–E06; E07 фиксирует недостающие сведения о версии и области проверки. Каждый вопрос имеет следующий шаг и критерий закрытия.

Завершена фиксация результатов двух проверок. Все I01–I08 и E01–E07 остаются открытыми. Исправления схем, нулевой ERC и готовность к изготовлению не подтверждены. Прочие пункты первого дня этим коммитом не закрываются.

## Результаты

- [Таблица 26 межплатных цепей](interboard-connections.md): точные имена на Control, существующие контакты Power, направления, источники и потребители, уровни и расхождения.
- [Фактическая распиновка CSV](interboard-pinout.csv): 64 контакта J400 и 21 контакт Power на J2301, J2603, J3302, J2602, J2502.
- [Исходные файлы и SHA-256](interboard-sources.json): 78 активных файлов схем, включённых в сверку.
- [Отчёты и разбор ERC](erc/README.md): исходные `.rpt`, все сообщения, группы причин и ограничения проверки.
- [Открытые вопросы](#open-questions): I01–I08 и E01–E07 с приоритетами и следующими действиями.

## Исходная версия и метод межплатной сверки

Базовая версия: [`b457c20`](https://github.com/max-talanov/mira/commit/b457c20e4a20e0389fd8b2b06486e559891e3b48) — `Replace Control with organized 30-page project`.

Отчёт сначала составлен по предоставленным архивам: актуальный Control из `MIRA_Control_Organized_1.zip`, Power из `hardware.zip`. Перед оформлением для GitHub все 30 активных файлов Control и все 48 активных файлов Power побайтово сопоставлены с указанным коммитом: различий нет. Архивные и не включённые в активную иерархию листы не использовались.

Соединения восстановлены по проводам, меткам и выводам символов в `.kicad_sch`. Все 64 контакта Control J400 дополнительно сверены с приложенным [FINAL.net.xml](../../hardware/MIRA_Control/docs/compliance/FINAL.net.xml). Для Power использован разбор текущих исходников. Свежий ERC в рамках межплатной сверки не запускался. Позднее полученные пользовательские отчёты разобраны [отдельно](erc/README.md); их происхождение и ограничения записаны там.

Напряжения в таблице взяты из схем и пояснений к ним. Это расчётные номиналы, а не измерения и не завершённая проверка допусков. Токи нагрузок, число силовых контактов, допустимые потери и режимы раздельного питания требуют дальнейшей проверки.

Сопоставления разъёмов, помеченные как кандидаты, не являются утверждённой схемой монтажа. Новые номера контактов Power не назначались.

<a id="open-questions"></a>

## Открытые вопросы

**P0:** блокирует зависимую работу или согласование интерфейса. **P1:** требуется проверка до размещения/разводки соответствующего узла. **P2:** оформление, не влияющее на электрическую работу. В этом перечне вопросов P2 нет.

| ID | Приоритет | Вопрос | Статус |
| --- | --- | --- | --- |
| I01 | P0 | Нет полной согласованной схемы соединения Power–Control | Открыт |
| I02 | P0 | Возврат аппаратной аварии MATRIX_INHIBIT_N не подключён к Power | Открыт |
| I03 | P0 | HOST_RESET_N не имеет межплатного вывода на Power | Открыт |
| I04 | P1 | HOST_ALIVE выведен из Control, но не принят на Power | Открыт |
| I05 | P1 | Согласовать роль AUX2V5 и критерий готовности всех шин | Открыт |
| I06 | P1 | Ток, допустимое падение и силовые контакты не подтверждены | Открыт |
| I07 | P1 | Проверить интерфейс при раздельном отключении доменов | Открыт |
| I08 | P1 | Подтвердить передачу VTT и DDR_VREF с Power на Control | Открыт |
| [E01](erc/README.md#e01) | P0 | Соединения обратной связи двух каналов U1903 | Открыт |
| [E02](erc/README.md#e02) | P1 | 85 сообщений об объектах вне сетки соединений | Открыт |
| [E03](erc/README.md#e03) | P1 | 34 предупреждения о VSS на отрицательном питании | Открыт |
| [E04](erc/README.md#e04) | P1 | 10 неоднозначных имён сетей со скрытыми выводами питания | Открыт |
| [E05](erc/README.md#e05) | P1 | Источники десяти сетей Power не распознаны ERC | Открыт |
| [E06](erc/README.md#e06) | P1 | Неподключённый #FLG0102 по отчёту Power | Открыт |
| [E07](erc/README.md#e07) | P1 | Версия, локальные исходники и область проверки ERC | Открыт |

Подробности, следующие действия и критерии для E01–E07 находятся в [разборе ERC](erc/README.md). Ниже сохранены полные карточки I01–I08.


### I01 — Нет полной согласованной схемы соединения Power–Control

**Приоритет:** P0. **Статус:** Открыт.

**Где:** Control: лист 400, J400. Power: J2301/J2603/J3302; источники питания 500–2200.

**Подтверждено схемой:** J400 имеет 64 контакта. 12 из 16 шин/опор не выведены на разъёмы Power. AON/SYS3V3 доступны на интерфейсных контактах, но силовой путь не согласован. Для MATRIX_PERMIT два разных источника.

**Следующее действие:** Выбрать общую пару разъёмов либо жгут/переходник. Внести на Power каждый обязательный вывод и таблицу соответствия. Для MATRIX_PERMIT выбрать AON или SYS3V3 выход.

**Критерий закрытия:** Для всех согласованных обязательных цепей есть схема физического соединения и контакты обеих плат. Решение об использовании HOST_ALIVE учитывает I04.

Исходники: [MIRA_Control: 400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch](../../hardware/MIRA_Control/400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch); [MIRA_Power: 2300_PROGRAM_INTERFACE.kicad_sch](../../hardware/MIRA_Power/2300_PROGRAM_INTERFACE.kicad_sch); [MIRA_Power: 2600_PM_PERMIT_INTERLOCKS.kicad_sch](../../hardware/MIRA_Power/2600_PM_PERMIT_INTERLOCKS.kicad_sch); [MIRA_Power: 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch](../../hardware/MIRA_Power/3300_PM_DEBUG_HOST_INTERFACE.kicad_sch).

### I02 — Возврат аппаратной аварии MATRIX_INHIBIT_N не подключён к Power

**Приоритет:** P0. **Статус:** Открыт.

**Где:** Control: 2200 Q2203; 400 J400.59. Power: 2600 J2602, U2602/U2603.

**Подтверждено схемой:** На Control открыт сток с AON-подтяжкой. На Power такого входа нет. J2602.2 — вход MATRIX STOP с 10k к AON, функциональный кандидат. J2603.2 MATRIX_KILL_H является выходом Power.

**Следующее действие:** Проверить подключение к MATRIX STOP или добавить отдельный вход. Закрепить полярность, защёлкивание, повторное разрешение и поведение при обрыве.

**Критерий закрытия:** LOW от Control аппаратно снимает MATRIX_PERMIT и программирующие шины по согласованной логике.

Исходники: [MIRA_Control: 2200_PROTECTION_MATRIX_TRIP_AND_FAULT_INTERFACE.kicad_sch](../../hardware/MIRA_Control/2200_PROTECTION_MATRIX_TRIP_AND_FAULT_INTERFACE.kicad_sch); [MIRA_Control: 400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch](../../hardware/MIRA_Control/400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch); [MIRA_Power: 2600_PM_PERMIT_INTERLOCKS.kicad_sch](../../hardware/MIRA_Power/2600_PM_PERMIT_INTERLOCKS.kicad_sch).

### I03 — HOST_RESET_N не имеет межплатного вывода на Power

**Приоритет:** P0. **Статус:** Открыт.

**Где:** Power: 2500 U2502.8, J2502.2. Control: 400 J400.58, 100 U100.33.

**Подтверждено схемой:** U2502.8 формирует HOST_RESET_N. J2502.2 соединён с U2502.3 MR_N, а не с RESET_N.

**Следующее действие:** Вывести U2502.8 на назначенный межплатный контакт и связать с J400.58. Подтверждение open-drain и подтяжек включить в I07.

**Критерий закрытия:** Отдельно обозначены MR_N и HOST_RESET_N; имеется однозначная связь с NRST MCU.

Исходники: [MIRA_Control: 100_MCU_POWER_CLOCKS_AND_DEBUG.kicad_sch](../../hardware/MIRA_Control/100_MCU_POWER_CLOCKS_AND_DEBUG.kicad_sch); [MIRA_Control: 400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch](../../hardware/MIRA_Control/400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch); [MIRA_Power: 2500_PM_WATCHDOGS.kicad_sch](../../hardware/MIRA_Power/2500_PM_WATCHDOGS.kicad_sch).

### I04 — HOST_ALIVE выведен из Control, но не принят на Power

**Приоритет:** P1. **Статус:** Открыт.

**Где:** Control: 300 U100.56/PB1, 400 J400.52; Power: 2400/3300.

**Подтверждено схемой:** HOST_WDI присутствует, отдельная цепь HOST_ALIVE на Power не найдена. На Control сигнал также используется внутри FPGA-интерфейса.

**Следующее действие:** Определить, нужен ли Power отдельный ALIVE помимо WDI/UART. Если нужен — выбрать вход MCU и контакт; если нет — явно отметить вывод как резерв и изменить контракт.

**Критерий закрытия:** Роль, направление и приёмник определены либо отсутствие межплатного использования документировано.

Исходники: [MIRA_Control: 300_MCU_QSPI_MICROSD_AND_CONTROL.kicad_sch](../../hardware/MIRA_Control/300_MCU_QSPI_MICROSD_AND_CONTROL.kicad_sch); [MIRA_Control: 400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch](../../hardware/MIRA_Control/400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch); [MIRA_Power: 2400_PM_CONTROLLER.kicad_sch](../../hardware/MIRA_Power/2400_PM_CONTROLLER.kicad_sch); [MIRA_Power: 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch](../../hardware/MIRA_Power/3300_PM_DEBUG_HOST_INTERFACE.kicad_sch).

### I05 — Согласовать роль AUX2V5 и критерий готовности всех шин

**Приоритет:** P1. **Статус:** Открыт.

**Где:** Power: 1400 AUX2V5, 3000 ALL_RAILS_PG. Control: 900 U903, PHY2V5.

**Подтверждено схемой:** На J400 нет AUX2V5. PHY2V5 на Control формируется локально U903 от IO3V3.

**Следующее действие:** Уточнить потребителя AUX2V5 на Power/системе и её участие в ALL_RAILS_PG. Не соединять AUX2V5 с выходом локального U903 без изменения архитектуры.

**Критерий закрытия:** Перечень обязательных шин и логика ALL_RAILS_PG соответствуют реальным потребителям.

Исходники: [MIRA_Control: 900_FPGA_ETHERNET_AND_MCU_INTERFACE.kicad_sch](../../hardware/MIRA_Control/900_FPGA_ETHERNET_AND_MCU_INTERFACE.kicad_sch); [MIRA_Power: 1400_FPGA_AUX_2V5.kicad_sch](../../hardware/MIRA_Power/1400_FPGA_AUX_2V5.kicad_sch); [MIRA_Power: 3000_PM_RAIL_READY.kicad_sch](../../hardware/MIRA_Power/3000_PM_RAIL_READY.kicad_sch).

### I06 — Ток, допустимое падение и силовые контакты не подтверждены

**Приоритет:** P1. **Статус:** Открыт.

**Где:** Control: J400. Power: шунты выходных шин 500–2000.

**Подтверждено схемой:** Параллельные контакты заданы только на Control. Номиналы питания на Power часто относятся к точке до шунта. Это не подтверждение напряжения на нагрузке.

**Следующее действие:** На втором дне составить бюджет токов; учесть шунты, дорожки, контакты и возврат GND. Проверить допуски всех нагрузок, включая FPGA AUX1V8/CORE1V0 и PHY VDD1P0. Выбрать конкретную пару разъёмов.

**Критерий закрытия:** Есть токи, допуски, расчёт падения и выбранные контакты/ответная часть.

Исходники: [MIRA_Control: 400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch](../../hardware/MIRA_Control/400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch); [MIRA_Power: 1200_POWER_MONITOR.kicad_sch](../../hardware/MIRA_Power/1200_POWER_MONITOR.kicad_sch); [MIRA_Power: 1300_FPGA_AUX_1V8.kicad_sch](../../hardware/MIRA_Power/1300_FPGA_AUX_1V8.kicad_sch); [MIRA_Power: 1700_PHY_1V05.kicad_sch](../../hardware/MIRA_Power/1700_PHY_1V05.kicad_sch).

### I07 — Проверить интерфейс при раздельном отключении доменов

**Приоритет:** P1. **Статус:** Открыт.

**Где:** Power: 2500 R2509, 3300 U3301. Control: 100 R106, 400 U400/U401.

**Подтверждено схемой:** Power буферизует статусы в SYS3V3; Control повторно принимает их в SYS3V3/IO3V3. RESET имеет 10k к AON и 10k к SYS3V3.

**Следующее действие:** Зафиксировать таблицу состояний AON/SYS3V3/IO3V3, проверить по datasheet уровни, Ioff, reset и обратное питание. Определить поведение UART/WDI и выбор MATRIX_PERMIT при выключенном SYS3V3.

**Критерий закрытия:** Для каждого состояния определены уровни, допустимые токи и безопасный сброс/запрет.

Исходники: [MIRA_Control: 100_MCU_POWER_CLOCKS_AND_DEBUG.kicad_sch](../../hardware/MIRA_Control/100_MCU_POWER_CLOCKS_AND_DEBUG.kicad_sch); [MIRA_Control: 400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch](../../hardware/MIRA_Control/400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch); [MIRA_Power: 2500_PM_WATCHDOGS.kicad_sch](../../hardware/MIRA_Power/2500_PM_WATCHDOGS.kicad_sch); [MIRA_Power: 3300_PM_DEBUG_HOST_INTERFACE.kicad_sch](../../hardware/MIRA_Power/3300_PM_DEBUG_HOST_INTERFACE.kicad_sch).

### I08 — Подтвердить передачу VTT и DDR_VREF с Power на Control

**Приоритет:** P1. **Статус:** Открыт.

**Где:** Power: 1800 U1801. Control: 800 DDR, J400.31/33.

**Подтверждено схемой:** Номинально оба равны DDR1V35/2, но VTT — силовая терминация, DDR_VREF — опора. В Power они пока не выведены.

**Следующее действие:** При выборе межплатной связи проверить source/sink, падение и петлю возврата VTT; шум и фильтрацию VREF; включение/выключение совместно с DDR1V35.

**Критерий закрытия:** Допуски на стороне DDR и маршрут возврата подтверждены до разводки DDR.

Исходники: [MIRA_Control: 800_FPGA_DDR3L_AND_REFERENCE_CLOCK.kicad_sch](../../hardware/MIRA_Control/800_FPGA_DDR3L_AND_REFERENCE_CLOCK.kicad_sch); [MIRA_Control: 400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch](../../hardware/MIRA_Control/400_SYSTEM_POWER_AND_SUPERVISION_INTERFACE.kicad_sch); [MIRA_Power: 1800_DDR_VTT_REFERENCE.kicad_sch](../../hardware/MIRA_Power/1800_DDR_VTT_REFERENCE.kicad_sch).

## Следующее действие

В актуальном Control открыть лист 1900 и проверить два соединения обратной связи U1903 по [E01](erc/README.md#e01). Дополнить версию и настройки запуска по [E07](erc/README.md#e07). После исправлений сохранять новые отчёты рядом с исходными, не подменяя историю проверки.

Для межплатного интерфейса начать с выбора схемы соединения I01, затем закрепить путь аппаратного запрета I02 и выход сброса I03. Вопросы закрываются после выполнения их критериев и фиксации исправлений в Git.
