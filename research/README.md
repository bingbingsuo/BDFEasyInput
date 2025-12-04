# BDF 输入格式研究目录

本目录用于存放 BDF 输入格式研究相关的文件和资料。

## 目录结构

```
research/
├── README.md                 # 本文件
├── bdf_examples/            # BDF 输入文件示例
│   ├── energy/              # 单点能计算示例
│   ├── optimize/            # 几何优化示例
│   ├── frequency/           # 频率计算示例
│   └── tddft/              # 激发态计算示例
├── mapping_tables/          # 映射表
│   ├── method_mapping.yaml
│   ├── basis_mapping.yaml
│   └── keyword_mapping.yaml
├── notes/                   # 研究笔记
│   ├── structure_analysis.md
│   ├── field_reference.md
│   └── findings.md
└── converted/              # 转换后的示例（用于验证）
```

## 使用说明

1. **收集示例**：将 BDF 输入文件示例放入 `bdf_examples/` 对应目录
2. **记录映射**：在 `mapping_tables/` 中建立和维护映射表
3. **记录笔记**：在 `notes/` 中记录研究发现
4. **验证转换**：在 `converted/` 中存放转换后的文件用于验证

## 研究流程

1. 收集 BDF 输入文件示例
2. 分析文件结构和格式
3. 建立映射关系
4. 验证映射正确性
5. 更新文档和映射表

