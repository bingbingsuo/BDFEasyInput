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
            r'\[Mulliken\s+Population\s+Analysis\].*?Atomic\s+charges:.*?(?=\n\n|\n\[|\n\|\||$)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if mulliken_section:
            section = mulliken_section.group(0)
            # 匹配格式：1O      -0.3061
            charges = {}
            charge_pattern = r'(\d+\w+)\s+([-+]?\d+\.\d+)'
            matches = re.finditer(charge_pattern, section)
            for match in matches:
                atom_label = match.group(1)
                charge = float(match.group(2))
                charges[atom_label] = charge
            if charges:
                properties['mulliken_charges'] = charges
        
        return properties

