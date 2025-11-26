# variant_9
Домашняя работа по конфигурационному управлению

## описание программы
Программа представляет собой парсер конфигурационных файлов специального формата с преобразованием в XML. Поддерживаются:

- **Двоичные числа**: `0b1010` (преобразуются в десятичные)
- **Строки**: `"text"` (поддерживают escape-последовательности)
- **Массивы**: `({ value1, value2, value3 })`
- **Константные выражения**: `^[ выражение ]` (вычисляются во время обработки)
- **Функции**: `sort()` (сортировка), `mod()` (остаток от деления)
- **Арифметические операции**: `+`, `-`, `*`, `/`
- **Многострочные комментарии**: `#= ... =#`

### базовый синтаксис:
имя <- значение

### примеры значений:
number <- 0b1101 # двоичное число (13 в десятичной)
text <- "Hello" # строка
array <- ({ 1, 2, 3 }) # массив
expr <- ^[ a + b ] # выражение

## запуск программы
python nine_variant.py -i build.cfg
python nine_variant.py -i recipe.cfg
python nine_variant.py -i network.

### обработка конфигурационного файла:
```bash
python nine_variant.py -i build.cfg
python nine_variant.py -i network.cfg
python nine_variant.py -i recipe.cfg
```

# требования
Python 3.6+
Стандартные библиотеки: sys, re, argparse, xml.etree.ElementTree

# пример вывода build.cfg
<config>
  <decl name="optlevel">
    <number>3</number>
  </decl><decl name="debug">
    <number>1</number>
  </decl><decl name="warning">
    <number>2</number>
  </decl><decl name="flags">
    <array>
      <item>
        <constexpr>3</constexpr>
      </item><item>
        <constexpr>1</constexpr>
      </item><item>
        <constexpr>2</constexpr>
      </item>
    </array>
  </decl><decl name="mask">
    <constexpr>6</constexpr>
  </decl><decl name="defines">
    <array>
      <item>
        <string>DEBUG</string>
      </item><item>
        <string>LOG</string>
      </item><item>
        <string>TRACE</string>
      </item>
    </array>
  </decl><decl name="sorteddefines">
    <constexpr>['DEBUG', 'LOG', 'TRACE']</constexpr>
  </decl><decl name="releasetag">
    <constexpr>1</constexpr>
  </decl>
</config>