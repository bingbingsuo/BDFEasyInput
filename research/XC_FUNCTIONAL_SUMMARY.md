# BDF XC 泛函处理总结

## 核心原则

**BDF 根据用户输入的泛函名直接匹配 libxc 的泛函，不做映射或重命名。**

## 支持的输入格式

### 1. 单一交换相关泛函

```yaml
method:
  type: dft
  functional: B3LYP
```

**BDF 输出**：
```bdf
dft functional
 B3LYP
```

### 2. 交换 + 相关 组合泛函

**字符串形式**：
```yaml
method:
  type: dft
  functional: "PBE LYP"
```

**结构化形式**：
```yaml
method:
  type: dft
  functional:
    x: PBE
    c: LYP
```

**BDF 输出**：
```bdf
dft functional
 PBE LYP
```

## 实现要点

1. **直接透传**：用户输入的泛函名原样传递给 BDF
2. **不做映射**：不进行任何名称转换或映射
3. **可选验证**：可以使用 libxc 列表进行验证（仅警告，不阻止）
4. **格式统一**：结构化输入统一转换为 "Xfun Cfun" 格式

## 相关文件

- **泛函列表**：`research/mapping_tables/xc_functionals.yaml`
- **使用指南**：`research/mapping_tables/xc_functional_guide.md`
- **生成工具**：`research/tools/generate_xc_functional_list.py`
- **查询工具**：`research/tools/query_xc_functionals.py`

## 统计信息

- **总泛函数**：678 个（来自 libxc）
- **泛函类型**：LDA, GGA, MGGA, HYB_GGA, HYB_MGGA, HYB_LDA
- **角色分类**：X（交换）, C（相关）, XC（交换相关）, K（动能）

---

**关键**：BDFEasyInput 不改变用户输入的泛函名，直接传递给 BDF，由 BDF 在 libxc 中匹配。

