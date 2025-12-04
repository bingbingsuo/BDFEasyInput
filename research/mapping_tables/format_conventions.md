# BDF 输入格式规范

## 大小写规则

### 已确认
- ✅ **模块名大小写不敏感**：`$COMPASS`、`$compass`、`$Compass` 都可以
- ✅ **关键词大小写不敏感**：`Title`、`title`、`TITLE` 都可以
- ✅ **BDF 会自动处理**：BDF 会自动标准化大小写

### 建议格式（为了可读性和一致性）

#### 模块名
- **使用大写**：`$COMPASS`、`$XUANYUAN`、`$SCF`、`$BDFOPT`、`$TDDFT`、`$RESP`、`$GRAD`
- **示例**：
  ```bdf
  $COMPASS
  $SCF
  $TDDFT
  ```

#### 关键词
- **使用首字母大写**：`Title`、`Basis`、`Geometry`、`Occupied`、`RHF`、`RKS`
- **示例**：
  ```bdf
  Title
  Basis
  Geometry
  ```

#### 模块结束标记
- **使用大写**：`$END`
- **示例**：
  ```bdf
  $END
  ```

## 格式规范总结

| 元素 | 建议格式 | 示例 | 说明 |
|------|----------|------|------|
| 模块名 | 全大写 | `$COMPASS` | 大小写不敏感，但建议大写 |
| 关键词 | 首字母大写 | `Title` | 大小写不敏感，但建议首字母大写 |
| 结束标记 | 全大写 | `$END` | 大小写不敏感，但建议大写 |
| 值 | 按原样 | `cc-pvdz` | 保持用户输入或标准格式 |

## 实现建议

在生成 BDF 输入文件时：

1. **统一使用标准格式**：
   - 模块名：`$COMPASS`、`$SCF` 等
   - 关键词：`Title`、`Basis`、`Geometry` 等
   - 结束标记：`$END`

2. **不依赖大小写敏感性**：
   - 虽然 BDF 不敏感，但使用标准格式
   - 提高生成文件的可读性
   - 便于用户理解和调试

3. **格式化函数**：
   ```python
   def format_module_name(name: str) -> str:
       """格式化模块名（统一使用大写）"""
       return f"${name.upper()}"
   
   def format_keyword(keyword: str) -> str:
       """格式化关键词（首字母大写）"""
       return keyword.capitalize()
   ```

## 示例对比

### 不推荐（虽然可以工作）
```bdf
$compass
title
 h2o
basis
 cc-pvdz
$end
```

### 推荐（标准格式）
```bdf
$COMPASS
Title
 H2O
Basis
 cc-pvdz
$END
```

---

**结论**：虽然 BDF 大小写不敏感，但使用标准格式可以提高可读性和一致性。

