"""
BDF Output File Parser

This module provides functionality to parse BDF output files and extract
key information such as energies, geometries, frequencies, etc.
"""

import re
from typing import Dict, List, Optional, Any
from pathlib import Path


class BDFOutputParser:
    """BDF 输出文件解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.energy_patterns = [
            # BDF 格式：E_tot = -76.02677205
            r'E_tot\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            # BDF 格式：Final scf result 下的 E_tot
            r'Final\s+scf\s+result.*?E_tot\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            # 通用格式
            r'Total\s+energy\s*[:=]\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            r'FINAL\s+ENERGY\s*[:=]\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            r'Total\s+SCF\s+energy\s*[:=]\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            r'SCF\s+energy\s*[:=]\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            r'E\(SCF\)\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
        ]
        
        self.scf_energy_patterns = [
            # BDF 格式：SCF Energy 列（迭代过程中）
            r'SCF\s+Energy\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            # BDF 格式：Final scf result 下的 E_ele
            r'Final\s+scf\s+result.*?E_ele\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            # 通用格式
            r'SCF\s+energy\s*[:=]\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            r'E\(SCF\)\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
        ]
        
        self.convergence_patterns = [
            # BDF 格式：正常终止
            r'Congratulations!\s+BDF\s+normal\s+termination',
            r'BDF\s+normal\s+termination',
            # 通用格式
            r'SCF\s+converged',
            r'CONVERGED',
            r'convergence\s+achieved',
            r'Optimization\s+converged',
            # BDF 格式：Final DeltaE 和 Final DeltaD 检查
            r'Final\s+DeltaE\s*=.*?Final\s+DeltaD\s*=',
        ]
        
        self.error_patterns = [
            r'ERROR',
            r'FATAL',
            r'ABORT',
            r'FAILED',
        ]
    
    def parse(self, output_file: str) -> Dict[str, Any]:
        """
        解析 BDF 输出文件
        
        Args:
            output_file: 输出文件路径
        
        Returns:
            包含解析结果的字典：
            {
                'energy': float,           # 总能量
                'scf_energy': float,       # SCF 能量
                'converged': bool,         # 是否收敛
                'geometry': List[Dict],    # 优化后的几何结构
                'frequencies': List[float], # 频率（如果有）
                'properties': Dict,        # 其他性质
                'warnings': List[str],     # 警告信息
                'errors': List[str]        # 错误信息
            }
        """
        output_path = Path(output_file)
        if not output_path.exists():
            raise FileNotFoundError(f"Output file not found: {output_file}")
        
        with open(output_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        result = {
            'energy': None,
            'scf_energy': None,
            'converged': False,
            'geometry': [],
            'frequencies': [],
            'properties': {},
            'optimization': {},
            'tddft': [],
            'warnings': [],
            'errors': [],
        }
        
        # 提取能量
        result['energy'] = self.extract_energy(content)
        result['scf_energy'] = self.extract_scf_energy(content)
        
        # 检查收敛性
        result['converged'] = self.check_convergence(content)
        
        # 提取几何结构
        result['geometry'] = self.extract_geometry(content)
        
        # 提取频率
        result['frequencies'] = self.extract_frequencies(content)
        
        # 提取额外性质
        result['properties'] = self.extract_properties(content)
        
        # 提取优化信息（如果有）
        result['optimization'] = self.extract_optimization_info(content)

        # 提取激发态信息（如果有，TDDFT）
        result['tddft'] = self.extract_tddft_calculations(content)
        # 兼容旧字段：若存在 TDDFT 结果则取第一段激发态，否则回退旧解析
        if result['tddft']:
            result['excited_states'] = result['tddft'][0].get('states', [])
        else:
            result['excited_states'] = self.extract_excited_states(content)
        
        # 提取警告和错误
        result['warnings'] = self.extract_warnings(content)
        result['errors'] = self.extract_errors(content)
        
        return result
    
    def extract_energy(self, content: str) -> Optional[float]:
        """提取总能量"""
        for pattern in self.energy_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None
    
    def extract_scf_energy(self, content: str) -> Optional[float]:
        """提取 SCF 能量"""
        # 优先使用 SCF 能量专用模式
        for pattern in self.scf_energy_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        # 尝试从迭代过程中提取最后的 SCF Energy
        # 格式：Iter. ... SCF Energy ... (最后一行)
        scf_iter_pattern = r'(\d+)\s+\d+\s+[\d.]+\s+([-+]?\d+\.\d+[Ee]?[-+]?\d*)'
        matches = list(re.finditer(scf_iter_pattern, content))
        if matches:
            # 取最后一行的能量
            last_match = matches[-1]
            try:
                return float(last_match.group(2))
            except (ValueError, IndexError):
                pass
        
        # 如果没有找到 SCF 能量，返回总能量
        return self.extract_energy(content)
    
    def check_convergence(self, content: str) -> bool:
        """检查计算是否收敛"""
        # 检查正常终止标志
        for pattern in self.convergence_patterns:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                return True
        
        # 检查 Final DeltaE 和 Final DeltaD（BDF 格式）
        # 如果 DeltaE 和 DeltaD 都很小，说明收敛
        deltae_match = re.search(r'Final\s+DeltaE\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)', content, re.IGNORECASE)
        deltad_match = re.search(r'Final\s+DeltaD\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)', content, re.IGNORECASE)
        
        if deltae_match and deltad_match:
            try:
                deltae = abs(float(deltae_match.group(1)))
                deltad = abs(float(deltad_match.group(1)))
                # 如果 DeltaE < 1e-6 且 DeltaD < 1e-4，认为收敛
                if deltae < 1e-6 and deltad < 1e-4:
                    return True
            except (ValueError, IndexError):
                pass
        
        # 检查是否有错误
        if self.extract_errors(content):
            return False
        
        return False
    
    def extract_geometry(self, content: str) -> List[Dict[str, Any]]:
        """
        提取几何结构
        
        Returns:
            原子坐标列表，每个元素为 {'element': str, 'x': float, 'y': float, 'z': float}
        """
        geometry = []
        
        # BDF 格式：Cartcoord(Bohr) 部分
        # 格式：Atom  Cartcoord(Bohr)  Charge Basis ...
        # 例如：O  0.000000  0.000000  0.221665  8.00 ...
        cartcoord_section = re.search(
            r'Atom\s+Cartcoord\(Bohr\).*?(?=\n\n|\n\[|\n\|\||$)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if cartcoord_section:
            section_content = cartcoord_section.group(0)
            # 匹配格式：O  0.000000  0.000000  0.221665  8.00 ...
            # 或：H  0.000000  1.430901  -0.886659  1.00 ...
            pattern = r'^\s*(\w+)\s+([-+]?\d+\.\d+)\s+([-+]?\d+\.\d+)\s+([-+]?\d+\.\d+)\s+\d+\.\d+'
            matches = re.finditer(pattern, section_content, re.MULTILINE)
            for match in matches:
                element = match.group(1)
                try:
                    x, y, z = float(match.group(2)), float(match.group(3)), float(match.group(4))
                    geometry.append({
                        'element': element,
                        'x': x,
                        'y': y,
                        'z': z,
                        'units': 'bohr'  # BDF 输出使用 Bohr 单位
                    })
                except ValueError:
                    continue
        
        # 如果没有找到，尝试查找优化后的几何结构
        if not geometry:
            # 查找 "Optimized geometry" 或 "Final geometry" 等关键词后的结构
            optimized_section = re.search(
                r'(?:Optimized|Final|Converged).*?geometry',
                content,
                re.IGNORECASE | re.DOTALL
            )
            
            if optimized_section:
                section_content = optimized_section.group(0)
                # 常见格式：原子符号后跟坐标
                geometry_pattern = r'(\w+)\s+([-+]?\d+\.?\d*)\s+([-+]?\d+\.?\d*)\s+([-+]?\d+\.?\d*)'
                matches = re.finditer(geometry_pattern, section_content)
                for match in matches:
                    element = match.group(1)
                    try:
                        x, y, z = float(match.group(2)), float(match.group(3)), float(match.group(4))
                        geometry.append({
                            'element': element,
                            'x': x,
                            'y': y,
                            'z': z,
                        })
                    except ValueError:
                        continue
        
        return geometry
    
    def extract_frequencies(self, content: str) -> List[float]:
        """提取频率（如果有）"""
        frequencies = []
        
        # BDF 格式：频率通常在 "Vibrational frequencies" 或类似部分
        # 格式可能是：频率值（cm-1）或频率值（Hz）
        
        # 查找频率部分（通常在 Hessian 计算后）
        freq_section_patterns = [
            r'Vibrational\s+frequencies.*?(?=\n\n|\n\[|\n\|\||$)',
            r'Normal\s+mode.*?frequencies.*?(?=\n\n|\n\[|\n\|\||$)',
            r'Frequency.*?analysis.*?(?=\n\n|\n\[|\n\|\||$)',
        ]
        
        freq_section = None
        for pattern in freq_section_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                freq_section = match.group(0)
                break
        
        # 如果在频率部分找到，提取频率值
        if freq_section:
            # 匹配频率值（通常是正数，单位 cm-1）
            # 格式：数字（可能带符号，虚频为负）
            freq_pattern = r'([-+]?\d+\.\d+)\s*cm[-1]|([-+]?\d+\.\d+)\s*Hz|([-+]?\d+\.\d+)(?=\s*(?:cm|Hz|wavenumber))'
            matches = re.finditer(freq_pattern, freq_section, re.IGNORECASE)
            for match in matches:
                for group in match.groups():
                    if group:
                        try:
                            freq = float(group)
                            frequencies.append(freq)
                        except ValueError:
                            continue
        
        # 如果没有找到频率部分，尝试通用模式
        if not frequencies:
            frequency_patterns = [
                r'Frequency\s*[:=]\s*([-+]?\d+\.?\d*)',
                r'Vibrational\s+frequency\s*[:=]\s*([-+]?\d+\.?\d*)',
                r'Freq\s*[:=]\s*([-+]?\d+\.?\d*)',
            ]
            
            for pattern in frequency_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    try:
                        freq = float(match.group(1))
                        frequencies.append(freq)
                    except (ValueError, IndexError):
                        continue
        
        return frequencies

    def extract_tddft_calculations(self, content: str) -> List[Dict[str, Any]]:
        """
        提取 TDDFT 计算块（支持多次计算，例如不同 isf/ialda）
        返回列表，每个元素包含元数据和对应激发态表
        """
        calculations: List[Dict[str, Any]] = []

        # 通过出现的 "Spin change:" 分割，每段到下一次出现或文件结尾
        spin_matches = list(re.finditer(r"Spin change\s*:", content, re.IGNORECASE))
        for idx, match in enumerate(spin_matches):
            start = match.start()
            end = spin_matches[idx + 1].start() if idx + 1 < len(spin_matches) else len(content)
            block = content[start:end]
            meta_block = block[:5000]  # 仅取当前块开头用于元数据，避免跨越到下一次 TDDFT 配置
            # 元数据检索范围：当前块开头，如缺失再向前回溯但不跨到后续块
            meta_scope_before = content[max(0, start - 100000):start]
            isf = None
            ialda = None
            itda = None
            method = None
            tda = False
            approximation_method = None

            isf_match = re.search(r'isf\s*=?\s*([+-]?\d+)', meta_block, re.IGNORECASE)
            if not isf_match:
                matches = list(re.finditer(r'isf\s*=?\s*([+-]?\d+)', meta_scope_before, re.IGNORECASE))
                isf_match = matches[-1] if matches else None
            if isf_match:
                try:
                    isf = int(isf_match.group(1))
                except ValueError:
                    isf = None

            ialda_match = re.search(r'ialda\s*=?\s*([+-]?\d+)', meta_block, re.IGNORECASE)
            if not ialda_match:
                matches = list(re.finditer(r'ialda\s*=?\s*([+-]?\d+)', meta_scope_before, re.IGNORECASE))
                ialda_match = matches[-1] if matches else None
            if ialda_match:
                try:
                    ialda = int(ialda_match.group(1))
                except ValueError:
                    ialda = None

            # 解析 itda 参数（TDA 近似标志）
            itda_match = re.search(r'itda\s*=?\s*(\d+)', meta_block, re.IGNORECASE)
            if not itda_match:
                matches = list(re.finditer(r'itda\s*=?\s*(\d+)', meta_scope_before, re.IGNORECASE))
                itda_match = matches[-1] if matches else None
            if itda_match:
                try:
                    itda = int(itda_match.group(1))
                except ValueError:
                    itda = None

            method_match = re.search(r'\[method\]\s*\n\s*([^\n]+)', meta_block, re.IGNORECASE)
            if not method_match:
                matches = list(re.finditer(r'\[method\]\s*\n\s*([^\n]+)', meta_scope_before, re.IGNORECASE))
                method_match = matches[-1] if matches else None
            if method_match:
                method = method_match.group(1).strip()

            # 确定是否使用 TDA 近似：
            # 1. 优先使用 itda 参数（最可靠）
            # 2. 如果没有 itda，检查 [method] 中是否明确标注 RPA 或 TDA
            # 3. 如果都没有，默认是 TDDFT (RPA)，因为 BDF 默认使用 RPA
            if itda is not None:
                tda = (itda == 1)
                if itda == 1:
                    approximation_method = "TDA (Tamm–Dancoff Approximation)"
                elif itda == 0:
                    approximation_method = "TDDFT (Time-Dependent Density Functional Theory)"
            else:
                # 如果没有找到 itda，检查 [method] 字段
                # 如果 method 中包含 "RPA"，明确是 TDDFT (RPA)
                # 注意：输出中可能同时提到 RPA 和 TDA（因为会显示两种方法的根数限制），
                # 但实际使用的方法应该从 [method] 字段判断
                if method:
                    # 检查 method 字段中是否明确标注了 RPA
                    if re.search(r'\bRPA\b', method, re.IGNORECASE):
                        tda = False
                        approximation_method = "TDDFT (Time-Dependent Density Functional Theory)"
                    elif re.search(r'\bTDA\b', method, re.IGNORECASE):
                        tda = True
                        approximation_method = "TDA (Tamm–Dancoff Approximation)"
                    else:
                        # 如果 method 中没有明确标识，默认是 TDDFT (RPA)
                        tda = False
                        approximation_method = "TDDFT (Time-Dependent Density Functional Theory)"
                else:
                    # 如果连 method 字段都没有，默认是 TDDFT (RPA)
                    # 因为 BDF 默认使用 RPA，只有明确指定 itda=1 才使用 TDA
                    tda = False
                    approximation_method = "TDDFT (Time-Dependent Density Functional Theory)"
            
            # 提取 JK 算符内存信息
            # 格式：Estimated memory for JK operator: 0.141 M
            jk_estimated_match = re.search(r'Estimated\s+memory\s+for\s+JK\s+operator:\s+([\d.]+)\s+M', meta_scope_before, re.IGNORECASE)
            jk_estimated_memory = None
            if jk_estimated_match:
                try:
                    jk_estimated_memory = float(jk_estimated_match.group(1))
                except ValueError:
                    pass
            
            # 格式：Maximum memory to calculate JK operator: 512.000 M
            jk_max_memory_match = re.search(r'Maximum\s+memory\s+to\s+calculate\s+JK\s+operator:\s+([\d.]+)\s+M', meta_scope_before, re.IGNORECASE)
            jk_max_memory = None
            if jk_max_memory_match:
                try:
                    jk_max_memory = float(jk_max_memory_match.group(1))
                except ValueError:
                    pass
            
            # 提取每次可计算的根数
            # 格式：Allow to calculate 2 roots at one pass for RPA
            rpa_roots_match = re.search(r'Allow\s+to\s+calculate\s+(\d+)\s+roots\s+at\s+one\s+pass\s+for\s+RPA', meta_scope_before, re.IGNORECASE)
            rpa_roots_per_pass = None
            if rpa_roots_match:
                try:
                    rpa_roots_per_pass = int(rpa_roots_match.group(1))
                except ValueError:
                    pass
            
            # 格式：Allow to calculate 4 roots at one pass for TDA
            tda_roots_match = re.search(r'Allow\s+to\s+calculate\s+(\d+)\s+roots\s+at\s+one\s+pass\s+for\s+TDA', meta_scope_before, re.IGNORECASE)
            tda_roots_per_pass = None
            if tda_roots_match:
                try:
                    tda_roots_per_pass = int(tda_roots_match.group(1))
                except ValueError:
                    pass
            
            # 提取用户要求的根数（Nexit）
            # 格式：Nexit: 4 (每个不可约表示计算的根数)
            nexit_match = re.search(r'Nexit:\s+(\d+)', meta_scope_before, re.IGNORECASE)
            n_exit = None
            if nexit_match:
                try:
                    n_exit = int(nexit_match.group(1))
                except ValueError:
                    pass
            
            # 根据是否使用TDA确定每次可计算的根数
            roots_per_pass = tda_roots_per_pass if tda else rpa_roots_per_pass

            states = self._parse_excited_states_block(block)
            calculations.append({
                'isf': isf,
                'ialda': ialda,
                'itda': itda,
                'method': method,
                'tda': tda,
                'approximation_method': approximation_method,
                'spin_flip_direction': 'down' if isf == -1 else ('up' if isf == 1 else None),
                'states': states,
                # JK 内存信息
                'jk_estimated_memory_mb': jk_estimated_memory,
                'jk_max_memory_mb': jk_max_memory,
                'rpa_roots_per_pass': rpa_roots_per_pass,
                'tda_roots_per_pass': tda_roots_per_pass,
                'roots_per_pass': roots_per_pass,
                'n_exit': n_exit,  # 用户要求的每个不可约表示的根数
            })

        return calculations

    def extract_excited_states(self, content: str) -> List[Dict[str, Any]]:
        """
        提取激发态能量与振子强度（TDDFT汇总表）

        解析汇总表格式（在行
        "No. Pair   ExSym   ExEnergies     Wavelengths      f ..."
        之后出现，空行分隔）
        """
        states: List[Dict[str, Any]] = []

        header = re.search(
            r"No\.\s+Pair\s+ExSym\s+ExEnergies\s+Wavelengths\s+f",
            content,
            re.IGNORECASE
        )
        if not header:
            return states

        # 从 header 位置开始，逐行解析直到遇到空行
        lines = content[header.start():].splitlines()
        # 跳过 header 行和紧随其后的空行
        start_idx = 0
        for i, line in enumerate(lines):
            if re.search(r"No\.\s+Pair\s+ExSym", line):
                start_idx = i + 1
                break

        started = False
        for line in lines[start_idx:]:
            if not line.strip():
                if started:
                    # 已经开始并遇到空行，结束
                    break
                else:
                    # 跳过开头的空行
                    continue
            started = True
            # 按空格切分列
            parts = line.split()
            # 期望格式:
            # idx, sym1, n1, sym2, energy_ev, eV, wavelength_nm, nm, f, dS2, rest...
            if len(parts) < 9:
                continue
            try:
                idx = int(parts[0])
                exsym = parts[1]  # 记录不可约表示
                energy_ev = float(parts[4])
                wavelength_nm = float(parts[6])
                osc = float(parts[8])
                d_s2 = float(parts[9]) if len(parts) > 9 else None
                dominant = " ".join(parts[10:]) if len(parts) > 10 else ""
                states.append({
                    'index': idx,
                    'symmetry': exsym,
                    'energy_ev': energy_ev,
                    'wavelength_nm': wavelength_nm,
                    'oscillator_strength': osc,
                    'delta_s2': d_s2,
                    'dominant': dominant.strip()
                })
            except (ValueError, IndexError):
                continue

        return states

    def _parse_excited_states_block(self, block: str) -> List[Dict[str, Any]]:
        """
        解析单个 TDDFT 块中的激发态表
        """
        states: List[Dict[str, Any]] = []

        lines = block.splitlines()
        start_idx = None
        for i, line in enumerate(lines):
            if re.search(r"No\.\s+Pair\s+ExSym", line):
                start_idx = i + 1
                break
        if start_idx is None:
            return states

        started = False
        for line in lines[start_idx:]:
            if not line.strip() or line.strip().startswith('***'):
                if started:
                    break
                else:
                    continue
            started = True
            parts = line.split()
            if len(parts) < 9:
                continue
            try:
                idx = int(parts[0])
                exsym = parts[1]
                energy_ev = float(parts[4])
                wavelength_nm = float(parts[6])
                osc = float(parts[8])
                d_s2 = float(parts[9]) if len(parts) > 9 else None
                dominant = " ".join(parts[10:]) if len(parts) > 10 else ""
                states.append({
                    'index': idx,
                    'symmetry': exsym,
                    'energy_ev': energy_ev,
                    'wavelength_nm': wavelength_nm,
                    'oscillator_strength': osc,
                    'delta_s2': d_s2,
                    'dominant': dominant.strip()
                })
            except (ValueError, IndexError):
                continue

        return states
    
    def extract_optimization_info(self, content: str) -> Dict[str, Any]:
        """
        提取结构优化信息
        
        Returns:
            包含优化信息的字典
        """
        opt_info = {
            'steps': [],
            'converged': False,
            'final_energy': None,
            'final_geometry': None,
            'convergence_criteria': {},
            'current_values': {},
        }
        
        # 检查是否有优化计算
        if not re.search(r'Geometry\s+Optimization|BDFOPT', content, re.IGNORECASE):
            return opt_info
        
        # 提取优化步骤
        step_pattern = r'Geometry\s+Optimization\s+step\s*:\s*(\d+)'
        steps = []
        for match in re.finditer(step_pattern, content, re.IGNORECASE):
            step_num = int(match.group(1))
            
            # 查找这一步的能量和梯度
            step_start = match.end()
            # 查找下一步或收敛检查
            next_step_match = re.search(r'Geometry\s+Optimization\s+step\s*:\s*(\d+)', content[step_start:], re.IGNORECASE)
            if next_step_match:
                step_end = step_start + next_step_match.start()
            else:
                step_end = len(content)
            
            step_content = content[step_start:step_end]
            
            # 提取这一步的能量
            energy_match = re.search(r'Energy\s*=\s*([-+]?\d+\.\d+)', step_content, re.IGNORECASE)
            energy = None
            if energy_match:
                try:
                    energy = float(energy_match.group(1))
                except (ValueError, IndexError):
                    pass
            
            # 提取梯度信息
            gradient_match = re.search(r'Gradient=\s*\n((?:\s+\w+\s+[-+]?\d+\.\d+\s+[-+]?\d+\.\d+\s+[-+]?\d+\.\d+\s*\n?)+)', step_content, re.IGNORECASE | re.MULTILINE)
            gradient = None
            if gradient_match:
                gradient_lines = gradient_match.group(1).strip().split('\n')
                gradient = []
                for line in gradient_lines:
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            gradient.append({
                                'atom': parts[0],
                                'x': float(parts[1]),
                                'y': float(parts[2]),
                                'z': float(parts[3]),
                            })
                        except (ValueError, IndexError):
                            pass
            
            steps.append({
                'step': step_num,
                'energy': energy,
                'gradient': gradient,
            })
        
        opt_info['steps'] = steps
        
        # 提取收敛信息
        # 查找包含收敛检查的更大范围（包括前面的收敛标准）
        converge_section = re.search(
            r'Conv\.\s+tolerance.*?Geom\.\s+converge\s*:.*?(?=\n\n|\n\w|\n\||$)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if converge_section:
            section = converge_section.group(0)
            
            # 检查是否收敛
            if re.search(r'Geom\.\s+converge\s*:.*?Yes', section, re.IGNORECASE):
                opt_info['converged'] = True
            
            # 提取收敛标准
            conv_tol_match = re.search(
                r'Conv\.\s+tolerance\s*:\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
                section,
                re.IGNORECASE
            )
            if conv_tol_match:
                try:
                    opt_info['convergence_criteria'] = {
                        'force_rms': float(conv_tol_match.group(1)),
                        'force_max': float(conv_tol_match.group(2)),
                        'step_rms': float(conv_tol_match.group(3)),
                        'step_max': float(conv_tol_match.group(4)),
                    }
                except (ValueError, IndexError):
                    pass
            
            # 提取当前值
            current_match = re.search(
                r'Current\s+values\s*:\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
                section,
                re.IGNORECASE
            )
            if current_match:
                try:
                    opt_info['current_values'] = {
                        'force_rms': float(current_match.group(1)),
                        'force_max': float(current_match.group(2)),
                        'step_rms': float(current_match.group(3)),
                        'step_max': float(current_match.group(4)),
                    }
                except (ValueError, IndexError):
                    pass
        
        # 提取最终能量（最后一步的能量）
        if steps:
            opt_info['final_energy'] = steps[-1].get('energy')
        
        # 提取最终几何结构（如果有）
        final_geom_match = re.search(
            r'Optimized\s+geometry|Final\s+geometry|Optimized\s+structure',
            content,
            re.IGNORECASE
        )
        if final_geom_match:
            # 尝试提取优化后的几何结构
            opt_info['final_geometry'] = self.extract_geometry(content)
        
        return opt_info
    
    def extract_warnings(self, content: str) -> List[str]:
        """提取警告信息"""
        warnings = []
        
        # 查找警告行
        warning_pattern = r'WARNING[:\s]+(.+)'
        matches = re.finditer(warning_pattern, content, re.IGNORECASE)
        
        for match in matches:
            warning = match.group(1).strip()
            if warning:
                warnings.append(warning)
        
        return warnings
    
    def extract_errors(self, content: str) -> List[str]:
        """提取错误信息"""
        errors = []
        
        # 查找错误行
        error_patterns = [
            r'ERROR[:\s]+(.+)',
            r'FATAL[:\s]+(.+)',
            r'ABORT[:\s]+(.+)',
        ]
        
        for pattern in error_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                error = match.group(1).strip()
                if error:
                    errors.append(error)
        
        return errors
    
    def extract_properties(self, content: str) -> Dict[str, Any]:
        """
        提取额外性质
        
        Returns:
            包含各种性质的字典
        """
        properties = {}
        
        # 提取能量分量（BDF 格式：Final scf result 部分）
        scf_result_section = re.search(
            r'Final\s+scf\s+result.*?(?=\n\n|\n\[|\n\|\||$)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if scf_result_section:
            section = scf_result_section.group(0)
            
            # 提取各种能量分量
            energy_components = {
                'E_tot': r'E_tot\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
                'E_ele': r'E_ele\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
                'E_nn': r'E_nn\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
                'E_1e': r'E_1e\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
                'E_ne': r'E_ne\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
                'E_kin': r'E_kin\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
                'E_ee': r'E_ee\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
                'E_xc': r'E_xc\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            }
            
            for key, pattern in energy_components.items():
                match = re.search(pattern, section, re.IGNORECASE)
                if match:
                    try:
                        properties[key] = float(match.group(1))
                    except (ValueError, IndexError):
                        pass
            
            # 提取 Virial Ratio
            virial_match = re.search(r'Virial\s+Ratio\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)', section, re.IGNORECASE)
            if virial_match:
                try:
                    properties['virial_ratio'] = float(virial_match.group(1))
                except (ValueError, IndexError):
                    pass
        
        # 提取 SCF 收敛标准（THRENE 和 THRDEN）
        threne_match = re.search(r'THRENE\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d+)', content, re.IGNORECASE)
        if threne_match:
            try:
                properties['scf_conv_thresh_ene'] = float(threne_match.group(1))
            except (ValueError, IndexError):
                pass
        
        thrden_match = re.search(r'THRDEN\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d+)', content, re.IGNORECASE)
        if thrden_match:
            try:
                properties['scf_conv_thresh_den'] = float(thrden_match.group(1))
            except (ValueError, IndexError):
                pass
        
        # 提取最终收敛值（Final DeltaE 和 Final DeltaD）
        deltae_match = re.search(r'Final\s+DeltaE\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)', content, re.IGNORECASE)
        if deltae_match:
            try:
                properties['final_deltae'] = float(deltae_match.group(1))
            except (ValueError, IndexError):
                pass
        
        deltad_match = re.search(r'Final\s+DeltaD\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)', content, re.IGNORECASE)
        if deltad_match:
            try:
                properties['final_deltad'] = float(deltad_match.group(1))
            except (ValueError, IndexError):
                pass
        
        # 提取 SCF 迭代次数
        # 格式：diis/vshift is closed at iter =   9
        # 注意：如果显示 iter = 9，实际SCF计算用了10次（iter 0到iter 9）
        diis_close_match = re.search(r'diis/vshift\s+is\s+closed\s+at\s+iter\s*=\s*(\d+)', content, re.IGNORECASE)
        if diis_close_match:
            try:
                iter_when_closed = int(diis_close_match.group(1))
                # 实际迭代次数 = iter_when_closed + 1（因为从0开始计数）
                properties['scf_iterations'] = iter_when_closed + 1
                properties['scf_iter_when_diis_closed'] = iter_when_closed
            except (ValueError, IndexError):
                pass
        
        # 提取溶剂效应信息
        solvent_section = re.search(
            r'\*Initializing\s+informations\s+for\s+solvent\s+effect\.\.\..*?(?=\n\n|\n\[|\n\|\||Check\s+basis|\n\s*\[init_smh\]|$)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if solvent_section:
            section = solvent_section.group(0)
            solvent_info = {}
            
            # 提取溶剂模型方法
            method_match = re.search(r'Method:\s*(\w+)', section, re.IGNORECASE)
            if method_match:
                solvent_info['method'] = method_match.group(1).strip()
            
            # 提取溶剂名称
            solvent_match = re.search(r'Solvent:\s*(\w+)', section, re.IGNORECASE)
            if solvent_match:
                solvent_info['solvent'] = solvent_match.group(1).strip()
            
            # 提取介电常数
            dielectric_match = re.search(r'Dielectric\s+constant:\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)', section, re.IGNORECASE)
            if dielectric_match:
                try:
                    solvent_info['dielectric_constant'] = float(dielectric_match.group(1))
                except (ValueError, IndexError):
                    pass
            
            # 提取光学介电常数
            optical_dielectric_match = re.search(r'Optical\s+dielectric\s+constant:\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)', section, re.IGNORECASE)
            if optical_dielectric_match:
                try:
                    solvent_info['optical_dielectric_constant'] = float(optical_dielectric_match.group(1))
                except (ValueError, IndexError):
                    pass
            
            # 提取镶嵌方法
            tessellation_match = re.search(r'Method\s+of\s+tessellation:\s*(\w+)', section, re.IGNORECASE)
            if tessellation_match:
                solvent_info['tessellation_method'] = tessellation_match.group(1).strip()
            
            # 提取半径类型
            radius_type_match = re.search(r'Type\s+of\s+Radius:\s*([^\n]+)', section, re.IGNORECASE)
            if radius_type_match:
                solvent_info['radius_type'] = radius_type_match.group(1).strip()
            
            # 提取网格精度
            mesh_accuracy_match = re.search(r'Accuracy\s+of\s+Mesh:\s*([^\n(]+)', section, re.IGNORECASE)
            if mesh_accuracy_match:
                solvent_info['mesh_accuracy'] = mesh_accuracy_match.group(1).strip()
            
            # 提取镶嵌数量
            tesseraes_match = re.search(r'Number\s+of\s+tesseraes:\s*(\d+)', section, re.IGNORECASE)
            if tesseraes_match:
                try:
                    solvent_info['num_tesseraes'] = int(tesseraes_match.group(1))
                except (ValueError, IndexError):
                    pass
            
            # 如果提取到了任何溶剂信息，添加到 properties 中
            if solvent_info:
                properties['solvent'] = solvent_info
        
        # 检查是否有隐式溶剂计算的提示（即使没有详细的溶剂信息部分）
        if re.search(r'Implicit\s+solvent\s+calculation\s+used', content, re.IGNORECASE):
            if 'solvent' not in properties:
                properties['solvent'] = {}
            properties['solvent']['implicit_solvent'] = True
        
        # 提取非平衡溶剂化校正信息（cLR）
        # 格式：
        # *State   1  ->  0
        #  Corrected vertical absorption energy               =    3.7217 eV
        #  Nonequilibrium solvation free energy               =   -0.0634 eV
        #  Equilibrium solvation free energy                  =   -0.1744 eV
        #  -------------------------------------------------------------------------------
        #  Excitation energy correction(cLR)                  =   -0.0377 eV
        noneq_pattern = re.compile(
            r'\*State\s+(\d+)\s+->\s+(\d+)\s*\n'
            r'\s*Corrected\s+vertical\s+absorption\s+energy\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s*eV\s*\n'
            r'\s*Nonequilibrium\s+solvation\s+free\s+energy\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s*eV\s*\n'
            r'\s*Equilibrium\s+solvation\s+free\s+energy\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s*eV\s*\n'
            r'(?:.*?\n)?\s*Excitation\s+energy\s+correction\(cLR\)\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s*eV',
            re.IGNORECASE
        )
        noneq_matches = list(noneq_pattern.finditer(content))
        if noneq_matches:
            corrections = []
            seen = set()
            for m in noneq_matches:
                try:
                    entry = {
                        'state_index': int(m.group(1)),
                        'to_state': int(m.group(2)),
                        'corrected_vertical_energy_ev': float(m.group(3)),
                        'noneq_solvation_free_energy_ev': float(m.group(4)),
                        'eq_solvation_free_energy_ev': float(m.group(5)),
                        'excitation_energy_correction_ev': float(m.group(6)),
                    }
                    key = tuple(entry.items())
                    if key in seen:
                        continue
                    seen.add(key)
                    corrections.append(entry)
                except (ValueError, IndexError):
                    continue
            if corrections:
                properties['solvent_noneq_corrections'] = corrections
                # 标记非平衡溶剂化方法为 state-specific (ptSS)
                properties['solvent_noneq_method'] = "ptSS_state_specific"
        
        # 如果未检测到 ptSS，但存在 solneqlr 关键字，标记为 cLR 线性响应
        if 'solvent_noneq_method' not in properties:
            if re.search(r'\bsolneqlr\b', content, re.IGNORECASE):
                properties['solvent_noneq_method'] = "clr_linear_response"
        
        # 提取 HOMO-LUMO gap
        # 格式：HOMO-LUMO gap:       0.13091934 au       3.56249790 eV
        gap_match = re.search(r'HOMO-LUMO\s+gap:\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+au\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+eV', content, re.IGNORECASE)
        if gap_match:
            try:
                properties['homo_lumo_gap'] = {
                    'au': float(gap_match.group(1)),
                    'ev': float(gap_match.group(2))
                }
            except (ValueError, IndexError):
                pass
        
        # 提取 HOMO 和 LUMO 轨道能量（Alpha 和 Beta）
        # 格式：Alpha   HOMO energy:      -0.24291496 au      -6.61005529 eV  Irrep: B2
        homo_alpha_match = re.search(r'Alpha\s+HOMO\s+energy:\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+au\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+eV', content, re.IGNORECASE)
        if homo_alpha_match:
            try:
                properties['homo_alpha'] = {
                    'au': float(homo_alpha_match.group(1)),
                    'ev': float(homo_alpha_match.group(2))
                }
            except (ValueError, IndexError):
                pass
        
        lumo_alpha_match = re.search(r'Alpha\s+LUMO\s+energy:\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+au\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+eV', content, re.IGNORECASE)
        if lumo_alpha_match:
            try:
                properties['lumo_alpha'] = {
                    'au': float(lumo_alpha_match.group(1)),
                    'ev': float(lumo_alpha_match.group(2))
                }
            except (ValueError, IndexError):
                pass
        
        homo_beta_match = re.search(r'Beta\s+HOMO\s+energy:\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+au\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+eV', content, re.IGNORECASE)
        if homo_beta_match:
            try:
                properties['homo_beta'] = {
                    'au': float(homo_beta_match.group(1)),
                    'ev': float(homo_beta_match.group(2))
                }
            except (ValueError, IndexError):
                pass
        
        lumo_beta_match = re.search(r'Beta\s+LUMO\s+energy:\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+au\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+eV', content, re.IGNORECASE)
        if lumo_beta_match:
            try:
                properties['lumo_beta'] = {
                    'au': float(lumo_beta_match.group(1)),
                    'ev': float(lumo_beta_match.group(2))
                }
            except (ValueError, IndexError):
                pass
        
        # 提取偶极矩（BDF 格式）
        dipole_section = re.search(
            r'\[Dipole\s+moment:.*?Totl:\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if dipole_section:
            try:
                properties['dipole'] = {
                    'x': float(dipole_section.group(1)),
                    'y': float(dipole_section.group(2)),
                    'z': float(dipole_section.group(3)),
                    'total': float(dipole_section.group(4)),
                    'units': 'Debye'
                }
            except (ValueError, IndexError):
                pass
        
        # 提取 Mulliken 布居分析
        mulliken_section = re.search(
            r'\[Mulliken\s+Population\s+Analysis\].*?(?=\n\s*\[|\n\n|\n\|\||$)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if mulliken_section:
            section = mulliken_section.group(0)
            # 匹配格式：1C      -0.1309    2.0149  (原子编号+元素符号, 电荷, 自旋密度)
            charges = {}
            spin_densities = {}
            # 匹配格式：    1C      -0.1309    2.0149
            charge_pattern = r'^\s*(\d+\w+)\s+([-+]?\d+\.\d+)\s+([-+]?\d+\.\d+)\s*$'
            matches = re.finditer(charge_pattern, section, re.MULTILINE)
            for match in matches:
                atom_label = match.group(1)
                charge = float(match.group(2))
                spin_density = float(match.group(3))
                charges[atom_label] = charge
                spin_densities[atom_label] = spin_density
            if charges:
                properties['mulliken_charges'] = charges
            if spin_densities:
                properties['mulliken_spin_densities'] = spin_densities
        
        # 提取 Lowdin 布居分析
        lowdin_section = re.search(
            r'\[Lowdin\s+Population\s+Analysis\].*?(?=\n\s*\[|\n\n|\n\|\||$)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if lowdin_section:
            section = lowdin_section.group(0)
            # 匹配格式：1C      -0.0189    1.9349  (原子编号+元素符号, 电荷, 自旋密度)
            charges = {}
            spin_densities = {}
            charge_pattern = r'^\s*(\d+\w+)\s+([-+]?\d+\.\d+)\s+([-+]?\d+\.\d+)\s*$'
            matches = re.finditer(charge_pattern, section, re.MULTILINE)
            for match in matches:
                atom_label = match.group(1)
                charge = float(match.group(2))
                spin_density = float(match.group(3))
                charges[atom_label] = charge
                spin_densities[atom_label] = spin_density
            if charges:
                properties['lowdin_charges'] = charges
            if spin_densities:
                properties['lowdin_spin_densities'] = spin_densities
        
        return properties

