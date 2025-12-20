# BDFEasyInput 工作流程图

## 完整工作流程图

```mermaid
graph TB
    Start([用户输入]) --> InputType{输入类型}
    
    InputType -->|自然语言| AIPlan[AI 任务规划]
    InputType -->|YAML/JSON| Validate[输入验证]
    
    AIPlan --> YAML[YAML 配置]
    YAML --> Validate
    
    Validate -->|验证通过| Convert[BDF 输入生成]
    Validate -->|验证失败| Error1[错误提示]
    
    Convert --> BDFInput[BDF 输入文件<br/>.inp]
    
    BDFInput --> RunOpt{是否执行?}
    RunOpt -->|是| Runner[计算执行]
    RunOpt -->|否| Parse
    
    Runner -->|直接执行| DirectRun[BDFDirectRunner]
    Runner -->|BDFAutotest| AutoTest[BDFAutotestRunner]
    
    DirectRun --> Output[BDF 输出文件]
    AutoTest --> Output
    
    Output --> Log[*.log<br/>主输出]
    Output --> Tmp[*.out.tmp<br/>每步SCF能量]
    Output --> Err[*.err<br/>错误信息]
    
    Log --> Parse[结果解析]
    Tmp --> Parse
    
    Parse --> ParsedData[解析数据]
    
    ParsedData --> Energy[能量信息<br/>E_tot, SCF, 分解]
    ParsedData --> Geometry[几何结构<br/>优化后坐标]
    ParsedData --> OptSteps[优化步骤<br/>SCF能量+收敛指标]
    ParsedData --> TDDFT[TDDFT信息<br/>激发态能量+优化]
    ParsedData --> Freq[频率信息<br/>振动频率+热力学]
    ParsedData --> Props[其他性质<br/>HOMO-LUMO, 偶极矩等]
    
    Energy --> AnalyzeOpt{是否AI分析?}
    Geometry --> AnalyzeOpt
    OptSteps --> AnalyzeOpt
    TDDFT --> AnalyzeOpt
    Freq --> AnalyzeOpt
    Props --> AnalyzeOpt
    
    AnalyzeOpt -->|是| AIAnalyzer[AI 分析器]
    AnalyzeOpt -->|否| ReportGen
    
    AIAnalyzer --> AIAnalysis[AI 分析结果<br/>专家级分析]
    AIAnalysis --> ReportGen[报告生成器]
    
    ReportGen --> Report[分析报告]
    
    Report --> Markdown[Markdown<br/>默认格式]
    Report --> HTML[HTML<br/>网页格式]
    Report --> Text[Text<br/>纯文本]
    
    Markdown --> End([最终结果])
    HTML --> End
    Text --> End
    
    Error1 --> End
    
    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style AIPlan fill:#fff9c4
    style Convert fill:#fff9c4
    style Runner fill:#ffccbc
    style Parse fill:#e1bee7
    style AIAnalyzer fill:#b2dfdb
    style ReportGen fill:#c5cae9
```

## 模块交互图

```mermaid
graph LR
    subgraph "用户接口层"
        CLI[CLI 命令行]
        API[Python API]
    end
    
    subgraph "核心功能层"
        Converter[转换器<br/>YAML→BDF]
        Validator[验证器<br/>参数检查]
        Runner[执行器<br/>运行计算]
        Parser[解析器<br/>输出解析]
    end
    
    subgraph "AI 辅助层"
        AIPlanner[AI 规划器<br/>任务规划]
        AIAnalyzer[AI 分析器<br/>结果分析]
        AIClients[AI 客户端<br/>9个服务商]
    end
    
    subgraph "BDF 模块生成"
        Compass[COMPASS<br/>结构+基组]
        SCF[SCF<br/>电子结构]
        TDDFT[TDDFT<br/>激发态]
        BDFOPT[BDFOPT<br/>优化]
        RESP[RESP<br/>梯度]
    end
    
    subgraph "报告生成"
        ReportGen[报告生成器]
        Markdown[Markdown]
        HTML[HTML]
    end
    
    CLI --> Converter
    CLI --> AIPlanner
    CLI --> Runner
    CLI --> Parser
    CLI --> AIAnalyzer
    
    API --> Converter
    API --> Runner
    API --> Parser
    
    AIPlanner --> AIClients
    AIAnalyzer --> AIClients
    
    Converter --> Validator
    Converter --> Compass
    Converter --> SCF
    Converter --> TDDFT
    Converter --> BDFOPT
    Converter --> RESP
    
    Runner --> Parser
    Parser --> AIAnalyzer
    AIAnalyzer --> ReportGen
    ReportGen --> Markdown
    ReportGen --> HTML
    
    style CLI fill:#e3f2fd
    style Converter fill:#fff9c4
    style Runner fill:#ffccbc
    style Parser fill:#e1bee7
    style AIPlanner fill:#b2dfdb
    style AIAnalyzer fill:#b2dfdb
    style ReportGen fill:#c5cae9
```

## 数据流图

```mermaid
flowchart TD
    subgraph "输入阶段"
        A1[自然语言描述] --> A2[YAML 配置]
        A3[YAML 文件] --> A2
    end
    
    subgraph "转换阶段"
        A2 --> B1[参数验证]
        B1 --> B2[BDF 模块生成]
        B2 --> B3[BDF 输入文件]
    end
    
    subgraph "执行阶段"
        B3 --> C1[BDF 计算]
        C1 --> C2[输出文件]
        C2 --> C3[*.log]
        C2 --> C4[*.out.tmp]
        C2 --> C5[*.err]
    end
    
    subgraph "解析阶段"
        C3 --> D1[输出解析器]
        C4 --> D1
        D1 --> D2[结构化数据]
        D2 --> D3[能量信息]
        D2 --> D4[几何结构]
        D2 --> D5[优化步骤]
        D2 --> D6[TDDFT 信息]
        D2 --> D7[频率信息]
    end
    
    subgraph "分析阶段"
        D3 --> E1[AI 分析器]
        D4 --> E1
        D5 --> E1
        D6 --> E1
        D7 --> E1
        E1 --> E2[AI 分析结果]
    end
    
    subgraph "报告阶段"
        D2 --> F1[报告生成器]
        E2 --> F1
        F1 --> F2[Markdown 报告]
        F1 --> F3[HTML 报告]
    end
    
    style A1 fill:#e1f5ff
    style B3 fill:#fff9c4
    style C2 fill:#ffccbc
    style D2 fill:#e1bee7
    style E2 fill:#b2dfdb
    style F2 fill:#c5cae9
```

## 优化步骤提取流程

```mermaid
graph TB
    Start([BDF 计算完成]) --> Log[读取 *.log 文件]
    Start --> Tmp[读取 *.out.tmp 文件]
    
    Log --> ExtractSteps[提取优化步骤]
    ExtractSteps --> StepInfo[步骤信息<br/>Force-RMS/Max<br/>Step-RMS/Max]
    
    Tmp --> ExtractSCF[提取 SCF 能量]
    ExtractSCF --> SCFEnergies[每步 SCF E_tot]
    
    Tmp --> ExtractTDDFT{是否TDDFT<br/>激发态优化?}
    ExtractTDDFT -->|是| ExtractGrad[提取 TDDFT 梯度]
    ExtractTDDFT -->|否| ExtractFinal
    
    ExtractGrad --> GradInfo[梯度信息<br/>ifile, irep, istate<br/>激发态 Etot]
    
    Tmp --> ExtractFinal[提取最终 SCF 结果]
    ExtractFinal --> FinalSCF[最终 SCF 能量分解<br/>E_tot, E_ele, E_nn<br/>E_1e, E_ne, E_kin<br/>E_ee, E_xc, Virial]
    
    StepInfo --> Combine[合并数据]
    SCFEnergies --> Combine
    GradInfo --> Combine
    FinalSCF --> Combine
    
    Combine --> BaseOpt{优化类型}
    BaseOpt -->|基态优化| BaseTable[基态优化步骤表<br/>Step | SCF Energy |<br/>Force-RMS | Force-Max |<br/>Step-RMS | Step-Max]
    BaseOpt -->|激发态优化| ExcTable[TDDFT 激发态优化表<br/>Step | SCF Energy | ifile |<br/>irep | istate | Excited Etot |<br/>Force-RMS | Force-Max |<br/>Step-RMS | Step-Max]
    
    BaseTable --> Report[报告生成]
    ExcTable --> Report
    FinalSCF --> Report
    
    Report --> End([分析报告])
    
    style Start fill:#e1f5ff
    style Combine fill:#fff9c4
    style BaseTable fill:#c8e6c9
    style ExcTable fill:#c8e6c9
    style Report fill:#c5cae9
    style End fill:#c8e6c9
```

## AI 模块工作流

```mermaid
graph TB
    Start([用户请求]) --> Type{请求类型}
    
    Type -->|任务规划| PlanFlow[规划流程]
    Type -->|结果分析| AnalyzeFlow[分析流程]
    
    subgraph PlanFlow[规划流程]
        PlanFlow --> P1[构建提示词]
        P1 --> P2[调用 AI 客户端]
        P2 --> P3[解析 AI 响应]
        P3 --> P4[生成 YAML 配置]
        P4 --> P5[方法推荐]
    end
    
    subgraph AnalyzeFlow[分析流程]
        AnalyzeFlow --> A1[解析输出文件]
        A1 --> A2[提取关键数据]
        A2 --> A3[构建分析提示词]
        A3 --> A4[调用 AI 客户端]
        A4 --> A5[解析 AI 分析]
        A5 --> A6[生成分析报告]
    end
    
    P2 --> AIClient[AI 客户端]
    A4 --> AIClient
    
    AIClient --> Provider{服务商}
    Provider -->|Ollama| Ollama[Ollama<br/>本地模型]
    Provider -->|OpenAI| OpenAI[OpenAI<br/>GPT-4/3.5]
    Provider -->|Anthropic| Anthropic[Anthropic<br/>Claude]
    Provider -->|OpenRouter| OpenRouter[OpenRouter<br/>统一接口]
    Provider -->|其他| Others[其他6个服务商]
    
    Ollama --> Response[AI 响应]
    OpenAI --> Response
    Anthropic --> Response
    OpenRouter --> Response
    Others --> Response
    
    Response --> P3
    Response --> A5
    
    P5 --> End1([YAML 配置])
    A6 --> End2([分析报告])
    
    style Start fill:#e1f5ff
    style AIClient fill:#b2dfdb
    style Response fill:#fff9c4
    style End1 fill:#c8e6c9
    style End2 fill:#c8e6c9
```

---

**说明**：这些流程图使用 Mermaid 语法，可以在支持 Mermaid 的 Markdown 查看器中直接渲染（如 GitHub、GitLab、VS Code 等）。
