# 分子坐标格式说明

## 坐标格式

BDFEasyInput 使用简洁的坐标格式，每行一个原子，格式为：

```
ATOM X Y Z
```

其中：
- `ATOM`: 原子符号（如 O, H, C, N 等）
- `X`, `Y`, `Z`: 三个坐标值（浮点数）

## 示例

### 水分子 (H2O)

```yaml
molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    # 坐标格式: ATOM X Y Z
    # 每行一个原子，格式为: 原子符号 X坐标 Y坐标 Z坐标
    # 单位由 molecule.units 指定（默认: angstrom）
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom  # 可选: angstrom 或 bohr，默认为 angstrom
```

### 苯分子 (C6H6)

```yaml
molecule:
  charge: 0
  multiplicity: 1
  coordinates:
    # 坐标格式: ATOM X Y Z
    # 每行一个原子，格式为: 原子符号 X坐标 Y坐标 Z坐标
    # 单位由 molecule.units 指定（默认: angstrom）
    - C  0.0000  1.3970 0.0000
    - C  1.2098  0.6985 0.0000
    - C  1.2098 -0.6985 0.0000
    - C  0.0000 -1.3970 0.0000
    - C -1.2098 -0.6985 0.0000
    - C -1.2098  0.6985 0.0000
    - H  0.0000  2.4810 0.0000
    - H  2.1490  1.2415 0.0000
    - H  2.1490 -1.2415 0.0000
    - H  0.0000 -2.4810 0.0000
    - H -2.1490 -1.2415 0.0000
    - H -2.1490  1.2415 0.0000
  units: angstrom  # 可选: angstrom 或 bohr，默认为 angstrom
```

## 单位

坐标单位通过 `molecule.units` 字段指定：

- `angstrom`: 埃（默认）
- `bohr`: 玻尔半径

```yaml
molecule:
  coordinates:
    # 坐标格式: ATOM X Y Z
    # 每行一个原子，格式为: 原子符号 X坐标 Y坐标 Z坐标
    - O  0.0000 0.0000 0.0000
    - H  0.9572 0.0000 0.0000
  units: angstrom  # 可选: angstrom 或 bohr，默认为 angstrom
```

**注意**：如果不指定 `units` 字段，默认使用 `angstrom`。

## 格式说明

1. **简洁性**：每行一个原子，格式简洁，易于阅读和编辑
2. **兼容性**：与常见的 XYZ 文件格式兼容
3. **灵活性**：支持任意数量的原子
4. **可读性**：可以使用注释说明原子

## 注意事项

1. **原子符号**：使用标准的元素符号（大写字母开头，如 O, H, C, N, Fe 等）
2. **坐标值**：支持正数和负数，可以是整数或浮点数
3. **顺序**：坐标顺序不影响计算结果，但建议按逻辑顺序排列
4. **注释**：可以使用 `#` 添加注释说明

## 从其他格式转换

### 从 XYZ 文件格式

XYZ 格式：
```
3
water
O  0.0000  0.0000  0.1173
H  0.0000  0.7572 -0.4692
H  0.0000 -0.7572 -0.4692
```

转换为 YAML：
```yaml
molecule:
  coordinates:
    # 坐标格式: ATOM X Y Z
    - O  0.0000 0.0000 0.1173
    - H  0.0000 0.7572 -0.4692
    - H  0.0000 -0.7572 -0.4692
  units: angstrom  # 可选: angstrom 或 bohr，默认为 angstrom
```

### 从旧格式转换

旧格式（已废弃）：
```yaml
coordinates:
  - atom: O
    x: 0.0
    y: 0.0
    z: 0.0
```

新格式：
```yaml
molecule:
  coordinates:
    # 坐标格式: ATOM X Y Z
    # 每行一个原子，格式为: 原子符号 X坐标 Y坐标 Z坐标
    - O  0.0000 0.0000 0.0000
    - H  0.9572 0.0000 0.0000
    - H -0.2398 0.9266 0.0000
  units: angstrom  # 可选: angstrom 或 bohr，默认为 angstrom
```

## 常见问题

**Q: 坐标顺序重要吗？**
A: 不重要，但建议按逻辑顺序排列（如先中心原子，再配位原子）

**Q: 可以使用科学计数法吗？**
A: 可以，如 `- O 1.0e-5 2.3e-4 0.0`

**Q: 支持哪些原子符号？**
A: 支持所有标准元素符号，包括过渡金属（如 Fe, Cu, Zn 等）

**Q: 坐标单位如何指定？**
A: 通过 `molecule.units` 字段指定，默认为 `angstrom`

