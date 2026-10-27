# Воспроизведение статической проверки

Распаковать `BASELINE_SCHEMATICS.zip` во временную папку. Внутри находятся
30 исходных листов и SHA256-манифест 100 исходных PCB/footprint/STEP-ресурсов.
Исходные названия и электрические связи соответствуют состоянию перед этим
обновлением CV/CC. Затем запустить из этого каталога:

```sh
python validate_compliance_project.py --baseline <распакованный_MIRA_Control> --working ../.. --baseline-net BASELINE.net.xml --final-net FINAL.net.xml --contract contracts/digital_contract_changes.json --contract contracts/routing_changes.json --contract contracts/fault_changes.json --contract contracts/2100_validation_manifest.json --output <временный_отчёт.json>
```

При установленном KiCad 10 актуальный `FINAL.net.xml` можно независимо
пересоздать командой `kicad-cli sch export netlist --format kicadxml` из
корневого `MIRA_Control.kicad_sch`. Проверка не изменяет проект. Соединения
сравниваются по полным группам физических выводов; наблюдённые изменения не
превращаются автоматически в разрешённые. Численные модели не являются
стендовыми измерениями или проверкой HDL.
