# 数据分析结果标准化设计

## 1. 设计目标

### 1.1 核心目标
- **标准化格式**：定义统一的数据结构，便于存储和复用
- **训练数据准备**：格式适合用于 LLM 模型训练
- **可扩展性**：支持未来添加新的分析维度
- **可追溯性**：保留完整的计算上下文信息

### 1.2 应用场景
- LLM 模型训练数据收集
- 分析结果对比和评估
- 知识库构建
- 结果复现和验证

## 2. 标准化数据格式

### 2.1 核心数据结构

```json
{
  "metadata": {
    "version": "1.0",
    "timestamp": "2024-01-15T10:30:00Z",
    "tool_version": "BDFEasyInput-0.1.0",
    "calculation_id": "calc_20240115_103000_h2o_pbe0"
  },
  "input": {
    "task_type": "energy",
    "molecule": {
      "formula": "H2O",
      "charge": 0,
      "multiplicity": 1,
      "coordinates": [
        {"atom": "O", "x": 0.0, "y": 0.0, "z": 0.1173},
        {"atom": "H", "x": 0.0, "y": 0.7572, "z": -0.4692},
        {"atom": "H", "x": 0.0, "y": -0.7572, "z": -0.4692}
      ],
      "units": "angstrom"
    },
    "method": {
      "type": "dft",
      "functional": "pbe0",
      "basis": "cc-pvdz"
    },
    "settings": {
      "scf": {
        "convergence": 1e-6,
        "max_iterations": 100
      }
    }
  },
  "execution": {
    "status": "success",
    "start_time": "2024-01-15T10:30:00Z",
    "end_time": "2024-01-15T10:35:23Z",
    "duration_seconds": 323,
    "bdf_version": "BDF-2.0",
    "output_file": "h2o_pbe0.out",
    "error_file": null
  },
  "raw_results": {
    "energy": {
      "total_energy": -76.41234567,
      "scf_energy": -76.41234567,
      "unit": "hartree"
    },
    "geometry": {
      "coordinates": [
        {"atom": "O", "x": 0.0, "y": 0.0, "z": 0.1173},
        {"atom": "H", "x": 0.0, "y": 0.7572, "z": -0.4692},
        {"atom": "H", "x": 0.0, "y": -0.7572, "z": -0.4692}
      ],
      "units": "angstrom"
    },
    "convergence": {
      "scf_converged": true,
      "scf_iterations": 12,
      "final_energy_change": 2.3e-7,
      "convergence_threshold": 1e-6
    },
    "properties": {
      "homo_energy": -0.5234,
      "lumo_energy": -0.1234,
      "homo_lumo_gap": 0.4000,
      "unit": "hartree"
    }
  },
  "analysis": {
    "summary": {
      "calculation_successful": true,
      "quality_assessment": "good",
      "main_findings": [
        "计算成功收敛",
        "总能量为 -76.4123 Hartree",
        "几何结构合理"
      ]
    },
    "energy_analysis": {
      "total_energy": -76.41234567,
      "energy_assessment": "合理",
      "comparison_with_literature": {
        "available": false,
        "reference_value": null,
        "deviation": null
      },
      "expert_comment": "总能量为负值，符合预期。SCF 迭代收敛良好。"
    },
    "geometry_analysis": {
      "bond_lengths": [
        {"atoms": ["O", "H"], "length": 0.9572, "unit": "angstrom", "assessment": "合理"},
        {"atoms": ["O", "H"], "length": 0.9572, "unit": "angstrom", "assessment": "合理"},
        {"atoms": ["H", "H"], "length": 1.5144, "unit": "angstrom", "assessment": "合理"}
      ],
      "bond_angles": [
        {"atoms": ["H", "O", "H"], "angle": 104.5, "unit": "degree", "assessment": "合理"}
      ],
      "symmetry": "C2v",
      "expert_comment": "几何结构合理，键长和键角在预期范围内，与实验值吻合良好。"
    },
    "convergence_analysis": {
      "scf_converged": true,
      "convergence_quality": "excellent",
      "iterations": 12,
      "final_energy_change": 2.3e-7,
      "expert_comment": "SCF 快速收敛，表明初始猜测良好。能量变化远小于阈值，计算可靠。"
    },
    "method_evaluation": {
      "functional": "pbe0",
      "basis": "cc-pvdz",
      "suitability": "appropriate",
      "recommendations": [
        "PBE0 是适合小分子的混合泛函",
        "cc-pVDZ 基组对水分子足够"
      ],
      "expert_comment": "方法选择合适，结果可靠。"
    },
    "recommendations": {
      "calculation_quality": "good",
      "further_calculations": [
        "如需更高精度，可考虑使用 cc-pVTZ 基组",
        "可进行频率计算验证结构为最小值"
      ],
      "improvements": []
    },
    "expert_insights": "本次计算成功完成了水分子的单点能计算。使用的 PBE0/cc-pVDZ 方法组合对于小分子体系是合适的选择。计算收敛良好，几何结构合理，与实验值吻合。总体而言，这是一个成功的计算，结果可以用于后续分析。"
  },
  "ai_analysis": {
    "model": {
      "provider": "ollama",
      "model_name": "llama3",
      "temperature": 0.7
    },
    "prompt_tokens": 1250,
    "completion_tokens": 850,
    "analysis_timestamp": "2024-01-15T10:35:25Z"
  }
}
```

### 2.2 训练数据格式（JSONL）

用于 LLM 训练的格式，每行一个 JSON 对象：

```jsonl
{"input": "计算水分子的单点能，使用 PBE0 方法和 cc-pVDZ 基组", "output": {"task": {"type": "energy"}, "molecule": {...}, "method": {...}}}
{"input": "优化苯分子的几何结构", "output": {"task": {"type": "optimize"}, "molecule": {...}, "method": {...}}}
```

或者用于结果分析的训练：

```jsonl
{"input": {"raw_results": {...}, "task_type": "energy"}, "output": {"analysis": {...}, "recommendations": [...]}}
```

## 3. 数据模式定义（Schema）

### 3.1 JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BDFEasyInput Analysis Result",
  "type": "object",
  "required": ["metadata", "input", "execution", "raw_results", "analysis"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["version", "timestamp", "calculation_id"],
      "properties": {
        "version": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"},
        "tool_version": {"type": "string"},
        "calculation_id": {"type": "string"}
      }
    },
    "input": {
      "type": "object",
      "required": ["task_type", "molecule", "method"],
      "properties": {
        "task_type": {
          "type": "string",
          "enum": ["energy", "optimize", "frequency", "tddft", "other"]
        },
        "molecule": {
          "type": "object",
          "required": ["formula", "charge", "multiplicity", "coordinates"],
          "properties": {
            "formula": {"type": "string"},
            "charge": {"type": "integer"},
            "multiplicity": {"type": "integer", "minimum": 1},
            "coordinates": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["atom", "x", "y", "z"],
                "properties": {
                  "atom": {"type": "string"},
                  "x": {"type": "number"},
                  "y": {"type": "number"},
                  "z": {"type": "number"}
                }
              }
            },
            "units": {
              "type": "string",
              "enum": ["angstrom", "bohr"],
              "default": "angstrom"
            }
          }
        },
        "method": {
          "type": "object",
          "required": ["type", "functional", "basis"],
          "properties": {
            "type": {"type": "string", "enum": ["dft", "hf", "mp2", "other"]},
            "functional": {"type": "string"},
            "basis": {"type": "string"}
          }
        }
      }
    },
    "execution": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["success", "failed", "timeout", "error"]
        },
        "start_time": {"type": "string", "format": "date-time"},
        "end_time": {"type": "string", "format": "date-time"},
        "duration_seconds": {"type": "number"},
        "bdf_version": {"type": "string"},
        "output_file": {"type": "string"},
        "error_file": {"type": ["string", "null"]}
      }
    },
    "raw_results": {
      "type": "object",
      "properties": {
        "energy": {
          "type": "object",
          "properties": {
            "total_energy": {"type": "number"},
            "scf_energy": {"type": "number"},
            "unit": {"type": "string", "default": "hartree"}
          }
        },
        "geometry": {
          "type": "object",
          "properties": {
            "coordinates": {
              "type": "array",
              "items": {
                "type": "object",
                "required": ["atom", "x", "y", "z"]
              }
            },
            "units": {"type": "string"}
          }
        },
        "convergence": {
          "type": "object",
          "properties": {
            "scf_converged": {"type": "boolean"},
            "scf_iterations": {"type": "integer"},
            "final_energy_change": {"type": "number"}
          }
        }
      }
    },
    "analysis": {
      "type": "object",
      "required": ["summary"],
      "properties": {
        "summary": {
          "type": "object",
          "required": ["calculation_successful", "quality_assessment"],
          "properties": {
            "calculation_successful": {"type": "boolean"},
            "quality_assessment": {
              "type": "string",
              "enum": ["excellent", "good", "fair", "poor"]
            },
            "main_findings": {
              "type": "array",
              "items": {"type": "string"}
            }
          }
        },
        "energy_analysis": {
          "type": "object",
          "properties": {
            "total_energy": {"type": "number"},
            "energy_assessment": {"type": "string"},
            "expert_comment": {"type": "string"}
          }
        },
        "geometry_analysis": {
          "type": "object",
          "properties": {
            "bond_lengths": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "atoms": {"type": "array", "items": {"type": "string"}},
                  "length": {"type": "number"},
                  "unit": {"type": "string"},
                  "assessment": {"type": "string"}
                }
              }
            },
            "expert_comment": {"type": "string"}
          }
        },
        "convergence_analysis": {
          "type": "object",
          "properties": {
            "scf_converged": {"type": "boolean"},
            "convergence_quality": {"type": "string"},
            "expert_comment": {"type": "string"}
          }
        },
        "method_evaluation": {
          "type": "object",
          "properties": {
            "functional": {"type": "string"},
            "basis": {"type": "string"},
            "suitability": {"type": "string"},
            "recommendations": {
              "type": "array",
              "items": {"type": "string"}
            },
            "expert_comment": {"type": "string"}
          }
        },
        "recommendations": {
          "type": "object",
          "properties": {
            "calculation_quality": {"type": "string"},
            "further_calculations": {
              "type": "array",
              "items": {"type": "string"}
            },
            "improvements": {
              "type": "array",
              "items": {"type": "string"}
            }
          }
        },
        "expert_insights": {"type": "string"}
      }
    },
    "ai_analysis": {
      "type": "object",
      "properties": {
        "model": {
          "type": "object",
          "properties": {
            "provider": {"type": "string"},
            "model_name": {"type": "string"},
            "temperature": {"type": "number"}
          }
        },
        "prompt_tokens": {"type": "integer"},
        "completion_tokens": {"type": "integer"},
        "analysis_timestamp": {"type": "string", "format": "date-time"}
      }
    }
  }
}
```

## 4. 数据标准化模块设计

### 4.1 模块结构

```
bdfeasyinput/
├── analysis/
│   ├── standardizer/        # ⭐ NEW 数据标准化模块
│   │   ├── __init__.py
│   │   ├── schema.py        # Schema 定义
│   │   ├── normalizer.py    # 数据标准化器
│   │   ├── validator.py     # 数据验证器
│   │   └── exporter.py      # 数据导出器
│   └── ...
```

### 4.2 标准化器接口

```python
from typing import Dict, Any, Optional
from pathlib import Path
import json
import jsonlines

class AnalysisStandardizer:
    """分析结果标准化器"""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        初始化标准化器
        
        Args:
            schema_path: JSON Schema 文件路径（可选）
        """
        self.schema = self.load_schema(schema_path) if schema_path else None
    
    def standardize(
        self,
        input_data: Dict,
        execution_result: Dict,
        raw_results: Dict,
        analysis_result: Dict,
        ai_metadata: Optional[Dict] = None
    ) -> Dict:
        """
        标准化分析结果
        
        Args:
            input_data: 输入数据（YAML 解析后的结果）
            execution_result: 执行结果
            raw_results: 原始计算结果
            analysis_result: AI 分析结果
            ai_metadata: AI 模型元数据
        
        Returns:
            标准化的数据字典
        """
        standardized = {
            "metadata": self._create_metadata(),
            "input": self._standardize_input(input_data),
            "execution": self._standardize_execution(execution_result),
            "raw_results": self._standardize_raw_results(raw_results),
            "analysis": self._standardize_analysis(analysis_result),
        }
        
        if ai_metadata:
            standardized["ai_analysis"] = self._standardize_ai_metadata(ai_metadata)
        
        # 验证数据
        if self.schema:
            self.validate(standardized)
        
        return standardized
    
    def validate(self, data: Dict) -> bool:
        """验证数据是否符合 Schema"""
        # 使用 jsonschema 验证
        pass
    
    def export_json(self, data: Dict, output_path: str) -> None:
        """导出为 JSON 文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def export_jsonl(self, data_list: list[Dict], output_path: str) -> None:
        """导出为 JSONL 文件（用于训练）"""
        with jsonlines.open(output_path, mode='w') as writer:
            for data in data_list:
                writer.write(data)
    
    def export_training_data(
        self,
        data_list: list[Dict],
        output_path: str,
        format: str = "jsonl"
    ) -> None:
        """
        导出训练数据
        
        Args:
            data_list: 标准化数据列表
            output_path: 输出路径
            format: 格式（jsonl, json, parquet）
        """
        if format == "jsonl":
            self.export_jsonl(data_list, output_path)
        elif format == "json":
            self.export_json(data_list, output_path)
        elif format == "parquet":
            # 使用 pandas 导出为 parquet
            pass
```

## 5. 训练数据准备

### 5.1 任务规划训练数据

```python
def prepare_planning_training_data(
    standardized_data_list: list[Dict]
) -> list[Dict]:
    """
    准备任务规划的训练数据
    
    格式: {"input": "自然语言描述", "output": {"task": {...}, "molecule": {...}}}
    """
    training_data = []
    
    for data in standardized_data_list:
        # 从 metadata 或单独存储中获取原始自然语言输入
        natural_language_input = data.get("metadata", {}).get("user_query", "")
        
        if natural_language_input:
            training_data.append({
                "input": natural_language_input,
                "output": {
                    "task": data["input"]["task_type"],
                    "molecule": data["input"]["molecule"],
                    "method": data["input"]["method"],
                    "settings": data["input"].get("settings", {})
                }
            })
    
    return training_data
```

### 5.2 结果分析训练数据

```python
def prepare_analysis_training_data(
    standardized_data_list: list[Dict]
) -> list[Dict]:
    """
    准备结果分析的训练数据
    
    格式: {"input": {"raw_results": {...}}, "output": {"analysis": {...}}}
    """
    training_data = []
    
    for data in standardized_data_list:
        training_data.append({
            "input": {
                "raw_results": data["raw_results"],
                "task_type": data["input"]["task_type"],
                "method": data["input"]["method"]
            },
            "output": {
                "analysis": data["analysis"],
                "recommendations": data["analysis"].get("recommendations", {})
            }
        })
    
    return training_data
```

## 6. 数据存储和管理

### 6.1 存储结构

```
data/
├── standardized/          # 标准化数据
│   ├── 2024/
│   │   ├── 01/
│   │   │   ├── calc_20240115_103000_h2o_pbe0.json
│   │   │   └── ...
│   └── ...
├── training/              # 训练数据
│   ├── planning/
│   │   ├── planning_data.jsonl
│   │   └── planning_data_metadata.json
│   ├── analysis/
│   │   ├── analysis_data.jsonl
│   │   └── analysis_data_metadata.json
│   └── ...
└── schemas/               # Schema 定义
    ├── analysis_result_schema.json
    └── training_data_schema.json
```

### 6.2 数据索引

```json
{
  "index_version": "1.0",
  "total_records": 1250,
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  },
  "statistics": {
    "task_types": {
      "energy": 800,
      "optimize": 300,
      "frequency": 150
    },
    "methods": {
      "pbe0": 500,
      "b3lyp": 400,
      "hf": 350
    }
  },
  "files": [
    {
      "id": "calc_20240115_103000_h2o_pbe0",
      "path": "2024/01/calc_20240115_103000_h2o_pbe0.json",
      "timestamp": "2024-01-15T10:30:00Z",
      "task_type": "energy",
      "molecule": "H2O",
      "method": "pbe0/cc-pvdz"
    }
  ]
}
```

## 7. 使用示例

### 7.1 标准化分析结果

```python
from bdfeasyinput.analysis.standardizer import AnalysisStandardizer

# 初始化标准化器
standardizer = AnalysisStandardizer()

# 标准化结果
standardized = standardizer.standardize(
    input_data=input_data,
    execution_result=execution_result,
    raw_results=raw_results,
    analysis_result=analysis_result,
    ai_metadata={"provider": "ollama", "model": "llama3"}
)

# 保存标准化数据
standardizer.export_json(standardized, "results/standardized/calc_001.json")
```

### 7.2 准备训练数据

```python
# 加载多个标准化数据
data_list = []
for file in Path("results/standardized").glob("*.json"):
    with open(file) as f:
        data_list.append(json.load(f))

# 准备训练数据
from bdfeasyinput.analysis.standardizer import prepare_planning_training_data

training_data = prepare_planning_training_data(data_list)

# 导出训练数据
standardizer.export_training_data(
    training_data,
    "data/training/planning_data.jsonl",
    format="jsonl"
)
```

### 7.3 批量处理

```python
# 批量标准化和导出
for result_file in result_files:
    # 加载结果
    result = load_result(result_file)
    
    # 标准化
    standardized = standardizer.standardize(**result)
    
    # 保存
    output_path = f"data/standardized/{standardized['metadata']['calculation_id']}.json"
    standardizer.export_json(standardized, output_path)
```

## 8. 数据质量保证

### 8.1 验证规则

- Schema 验证：确保数据结构符合定义
- 数据完整性：检查必需字段
- 数据一致性：验证数值范围和逻辑关系
- 单位一致性：确保单位使用正确

### 8.2 数据清洗

- 移除无效数据
- 处理缺失值
- 标准化格式（日期、数值精度等）
- 去重处理

## 9. 隐私和安全

### 9.1 数据脱敏

- 移除敏感信息
- 匿名化处理
- 数据加密（如需要）

### 9.2 访问控制

- 数据访问权限管理
- 数据使用协议
- 合规性检查

## 10. 实施计划

### Phase 1: 基础标准化（2-3 周）
- [ ] 定义数据 Schema
- [ ] 实现标准化器
- [ ] 实现验证器
- [ ] 基础导出功能

### Phase 2: 训练数据准备（2-3 周）
- [ ] 训练数据格式设计
- [ ] 数据提取和转换
- [ ] 批量处理功能
- [ ] 数据索引系统

### Phase 3: 数据管理（2-3 周）
- [ ] 数据存储系统
- [ ] 数据查询和检索
- [ ] 数据统计和分析
- [ ] 数据质量监控

