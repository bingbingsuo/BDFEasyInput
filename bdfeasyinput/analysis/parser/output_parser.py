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
        
        # 提取频率（现在返回字典，包含振动和平动/转动频率）
        freq_data = self.extract_frequencies(content)
        result['frequencies'] = freq_data.get('all', [])  # 向后兼容：保持列表格式
        result['frequency_data'] = freq_data  # 新的结构化数据
        
        # 提取额外性质
        result['properties'] = self.extract_properties(content)
        
        # 提取SCF方法类型（如果有）
        scf_method = self.extract_scf_method(content)
        if scf_method:
            result['properties']['scf_method'] = scf_method
        
        # 提取热力学数据
        thermochemistry = self.extract_thermochemistry(content)
        if thermochemistry:
            result['properties']['thermochemistry'] = thermochemistry
        
        # 提取优化信息（如果有）
        result['optimization'] = self.extract_optimization_info(content)
        
        # 如果存在优化步骤，尝试从 *.out.tmp 文件中提取每一步的 SCF 能量
        if result['optimization'].get('steps'):
            out_tmp_file = output_path.with_suffix('.out.tmp')
            if out_tmp_file.exists():
                scf_energies = self.extract_scf_energies_from_tmp(str(out_tmp_file))
                # 将 SCF 能量合并到优化步骤中
                for i, step in enumerate(result['optimization']['steps']):
                    if i < len(scf_energies):
                        step['scf_energy'] = scf_energies[i]
                
                # 提取最后一次 SCF 的能量分解信息
                final_scf_components = self.extract_final_scf_energy_components(str(out_tmp_file))
                if final_scf_components:
                    result['properties']['final_scf_components'] = final_scf_components

        # 提取激发态信息（如果有，TDDFT）
        result['tddft'] = self.extract_tddft_calculations(content)
        # 兼容旧字段：若存在 TDDFT 结果则取第一段激发态，否则回退旧解析
        if result['tddft']:
            result['excited_states'] = result['tddft'][0].get('states', [])
        else:
            result['excited_states'] = self.extract_excited_states(content)
        
        # 提取resp模块的激发态梯度计算信息（如果有）
        resp_gradient_info = self.extract_resp_gradient_info(content)
        if resp_gradient_info:
            result['properties']['resp_gradient'] = resp_gradient_info

        # 提取对称群信息（如果有）
        symmetry_info = self.extract_symmetry_info(content)
        if symmetry_info:
            result['properties']['symmetry'] = symmetry_info

        # 提取不可约表示和分子轨道信息（如果有）
        irrep_info = self.extract_irrep_info(content)
        if irrep_info:
            result['properties']['irreps'] = irrep_info

        # 提取轨道占据信息（如果有）
        # 注意：需要先提取SCF方法信息，以便正确判断限制性/非限制性方法
        # 直接使用上面提取的scf_method变量，而不是从result中重新获取
        occupation_info = self.extract_occupation_info(content, scf_method=scf_method)
        if occupation_info:
            result['properties']['occupation'] = occupation_info

        # 提取SCF State symmetry（如果有）
        scf_state_symmetry = self.extract_scf_state_symmetry(content)
        if scf_state_symmetry:
            result['properties']['scf_state_symmetry'] = scf_state_symmetry

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
        提取几何结构（优化版本，提高精度）
        
        Returns:
            原子坐标列表，每个元素为 {
                'element': str,      # 元素符号
                'x': float,          # X坐标
                'y': float,          # Y坐标
                'z': float,          # Z坐标
                'units': str,        # 单位 ('bohr' 或 'angstrom')
                'index': int,        # 原子索引（如果可提取）
                'charge': float      # 原子电荷（如果可提取）
            }
        """
        geometry = []
        
        # 策略0: 最高优先级 - 提取结构优化后的几何结构（Angstrom单位）
        # 支持收敛和未收敛两种情况
        # 查找所有 "Molecular Cartesian Coordinates (X,Y,Z) in Angstrom :" 出现的位置
        coords_matches = list(re.finditer(
            r'Molecular\s+Cartesian\s+Coordinates\s+\(X,Y,Z\)\s+in\s+Angstrom\s*:.*?(?=\n\n|\n\s+Force-RMS|\n\s+Redundant|\Z)',
            content,
            re.IGNORECASE | re.DOTALL
        ))
        
        if coords_matches:
            # 使用最后一个匹配（最终优化结构，无论是否收敛）
            last_match = coords_matches[-1]
            section_content = last_match.group(0)
            
            # 检查是否收敛
            is_converged = False
            # 检查收敛提示（在当前section或之后）
            match_end = last_match.end()
            # 在当前section中查找收敛信息
            if re.search(r'Geom\.\s+converge\s*:.*?Yes', section_content, re.IGNORECASE):
                is_converged = True
            elif re.search(r'Good\s+Job,\s+Geometry\s+Optimization\s+converged', content[:match_end], re.IGNORECASE):
                is_converged = True
            # 检查未收敛提示
            elif re.search(r'Geometry\s+Optimization\s+not\s+converged', content[:match_end], re.IGNORECASE):
                is_converged = False
            
            # 提取坐标部分（跳过标题行）
            coords_start = re.search(
                r'Molecular\s+Cartesian\s+Coordinates\s+\(X,Y,Z\)\s+in\s+Angstrom\s*:',
                section_content,
                re.IGNORECASE
            )
            
            if coords_start:
                coords_section = section_content[coords_start.end():].strip()
                # 匹配格式：元素符号 + 三个坐标（支持科学计数法）
                # 例如：C           1.12766281      -0.06079459       1.22640622
                pattern = r'^\s*(\w+)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)'
                matches = re.finditer(pattern, coords_section, re.MULTILINE)
                
                for idx, match in enumerate(matches, start=1):
                    element = match.group(1).strip()
                    # 跳过可能的表头或空行
                    if not element or element.upper() in ['MOLECULAR', 'CARTESIAN', 'COORDINATES', 'ANGSTROM']:
                        continue
                    
                    try:
                        x = float(match.group(2))
                        y = float(match.group(3))
                        z = float(match.group(4))
                        
                        geometry.append({
                            'element': element,
                            'x': x,
                            'y': y,
                            'z': z,
                            'units': 'angstrom',  # 优化后的结构使用 Angstrom 单位
                            'index': idx,
                            'optimized': True,  # 标记为优化后的结构
                            'converged': is_converged  # 根据实际收敛状态设置
                        })
                    except (ValueError, IndexError):
                        continue
        
        # 如果已经提取到优化后的结构（Angstrom单位），就不再提取Cartcoord
        # 因为优化后的结构是最终结构，优先级更高
        if geometry and geometry[0].get('units') == 'angstrom' and geometry[0].get('optimized'):
            return geometry
        
        # 策略1: 提取最后的 Cartcoord(Bohr) 部分（最终几何结构）
        # 查找所有 Cartcoord(Bohr) 部分，取最后一个
        cartcoord_matches = list(re.finditer(
            r'Atom\s+Cartcoord\(Bohr\).*?(?=\n\n|\n\[|\n\|\||\nAtom\s+Cartcoord|$)',
            content,
            re.IGNORECASE | re.DOTALL
        ))
        
        if cartcoord_matches:
            # 使用最后一个匹配（最终几何结构）
            last_section = cartcoord_matches[-1]
            section_content = last_section.group(0)
            
            # 改进的正则表达式：更精确匹配坐标行
            # 格式：元素符号 + 三个坐标（支持科学计数法）+ 电荷（可选）
            # 例如：C        0.000000     0.000000     0.313990     6.00 ...
            # 或：  H        0.000000    -1.657230    -0.941970     1.00 ...
            pattern = r'^\s*(\w+)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)(?:\s+([-+]?\d+\.?\d*))?'
            matches = re.finditer(pattern, section_content, re.MULTILINE)
            
            for idx, match in enumerate(matches, start=1):
                element = match.group(1).strip()
                # 跳过表头行（如果元素符号不是真正的元素）
                if element.upper() in ['ATOM', 'CARTCOORD', 'CHARGE', 'BASIS']:
                    continue
                
                try:
                    x = float(match.group(2))
                    y = float(match.group(3))
                    z = float(match.group(4))
                    charge = float(match.group(5)) if match.group(5) else None
                    
                    geometry.append({
                        'element': element,
                        'x': x,
                        'y': y,
                        'z': z,
                        'units': 'bohr',  # BDF 输出使用 Bohr 单位
                        'index': idx,
                        'charge': charge
                    })
                except (ValueError, IndexError):
                    continue
        
        # 策略2: 如果没有找到 Cartcoord，尝试查找其他格式的几何结构
        if not geometry:
            # 查找 "Optimized geometry" 或 "Final geometry" 等关键词后的结构
            optimized_section = re.search(
                r'(?:Optimized|Final|Converged).*?geometry.*?(?=\n\n|\n\[|\n\|\||$)',
                content,
                re.IGNORECASE | re.DOTALL
            )
            
            if optimized_section:
                section_content = optimized_section.group(0)
                # 匹配格式：原子符号后跟坐标（支持科学计数法）
                geometry_pattern = r'(\w+)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)'
                matches = re.finditer(geometry_pattern, section_content)
                for idx, match in enumerate(matches, start=1):
                    element = match.group(1)
                    # 跳过关键词行
                    if element.lower() in ['optimized', 'final', 'converged', 'geometry']:
                        continue
                    try:
                        x, y, z = float(match.group(2)), float(match.group(3)), float(match.group(4))
                        geometry.append({
                            'element': element,
                            'x': x,
                            'y': y,
                            'z': z,
                            'units': 'bohr',  # 默认假设为 Bohr
                            'index': idx
                        })
                    except ValueError:
                        continue
        
        # 策略3: 尝试从输入文件格式的几何结构部分提取
        if not geometry:
            # 查找 Geometry ... End geometry 块
            geometry_block = re.search(
                r'Geometry\s*\n(.*?)End\s+geometry',
                content,
                re.IGNORECASE | re.DOTALL
            )
            
            if geometry_block:
                block_content = geometry_block.group(1)
                # 匹配格式：元素符号 X Y Z
                pattern = r'(\w+)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)'
                matches = re.finditer(pattern, block_content)
                for idx, match in enumerate(matches, start=1):
                    element = match.group(1)
                    if element.lower() in ['geometry', 'end']:
                        continue
                    try:
                        x, y, z = float(match.group(2)), float(match.group(3)), float(match.group(4))
                        geometry.append({
                            'element': element,
                            'x': x,
                            'y': y,
                            'z': z,
                            'units': 'bohr',  # 需要根据输入文件判断，默认 Bohr
                            'index': idx
                        })
                    except ValueError:
                        continue
        
        return geometry
    
    def format_geometry_for_input(self, geometry: List[Dict[str, Any]], units: str = 'angstrom') -> str:
        """
        格式化几何结构为下一步计算的输入格式
        
        Args:
            geometry: 几何结构列表（从 extract_geometry 获取）
            units: 输出单位，'angstrom' 或 'bohr'（默认 'angstrom'）
        
        Returns:
            格式化后的几何结构字符串，每行格式：元素符号 X Y Z（8位小数）
        """
        if not geometry:
            return ""
        
        # 转换单位（如果需要）
        conversion_factor = 1.0
        if units == 'angstrom':
            # 如果输入是 bohr，转换为 angstrom
            if geometry[0].get('units') == 'bohr':
                conversion_factor = 0.529177  # 1 Bohr = 0.529177 Angstrom
        elif units == 'bohr':
            # 如果输入是 angstrom，转换为 bohr
            if geometry[0].get('units') == 'angstrom':
                conversion_factor = 1.8897259886  # 1 Angstrom = 1.8897259886 Bohr
        
        lines = []
        for atom in geometry:
            element = atom.get('element', '')
            x = atom.get('x', 0.0) * conversion_factor
            y = atom.get('y', 0.0) * conversion_factor
            z = atom.get('z', 0.0) * conversion_factor
            
            # 格式：元素符号 + 三个坐标（8位小数，右对齐）
            line = f"{element:>3s}  {x:15.8f}  {y:15.8f}  {z:15.8f}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def extract_frequencies(self, content: str) -> Dict[str, Any]:
        """
        提取频率（如果有）
        
        Returns:
            包含振动频率和平动/转动频率的字典：
            {
                'vibrations': [频率列表],
                'translations_rotations': [频率列表],
                'all': [所有频率列表]  # 为了向后兼容
            }
        """
        vibrations = []
        translations_rotations = []
        
        # BDF 格式：区分 "Results of vibrations:" 和 "Results of translations and rotations:"
        
        # 提取振动频率部分
        vib_section_match = re.search(
            r'Results\s+of\s+vibrations:.*?(?=Results\s+of\s+translations|$)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if vib_section_match:
            vib_section = vib_section_match.group(0)
            # 在振动部分查找 "Frequencies" 行
            freq_line_pattern = r'^\s*Frequencies\s+([-+]?\d+\.\d+(?:\s+[-+]?\d+\.\d+)*)'
            matches = re.finditer(freq_line_pattern, vib_section, re.IGNORECASE | re.MULTILINE)
            seen = set()
            for match in matches:
                freq_line = match.group(1)
                freq_values = re.findall(r'([-+]?\d+\.\d+)', freq_line)
                for freq_str in freq_values:
                    try:
                        freq = float(freq_str)
                        if freq not in seen:
                            vibrations.append(freq)
                            seen.add(freq)
                    except ValueError:
                        continue
        
        # 提取平动/转动频率部分
        trans_rot_section_match = re.search(
            r'Results\s+of\s+translations\s+and\s+rotations:.*?(?=\n\s*\*\*\*|Thermal\s+Contributions|\n\s*\[|$)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if trans_rot_section_match:
            trans_rot_section = trans_rot_section_match.group(0)
            # 在平动/转动部分查找 "Frequencies" 行
            freq_line_pattern = r'^\s*Frequencies\s+([-+]?\d+\.\d+(?:\s+[-+]?\d+\.\d+)*)'
            matches = re.finditer(freq_line_pattern, trans_rot_section, re.IGNORECASE | re.MULTILINE)
            seen = set()
            for match in matches:
                freq_line = match.group(1)
                freq_values = re.findall(r'([-+]?\d+\.\d+)', freq_line)
                for freq_str in freq_values:
                    try:
                        freq = float(freq_str)
                        if freq not in seen:
                            translations_rotations.append(freq)
                            seen.add(freq)
                    except ValueError:
                        continue
        
        # 如果没有找到明确的分区，尝试通用方法（向后兼容）
        if not vibrations and not translations_rotations:
            freq_line_pattern = r'^\s*Frequencies\s+([-+]?\d+\.\d+(?:\s+[-+]?\d+\.\d+)*)'
            matches = re.finditer(freq_line_pattern, content, re.IGNORECASE | re.MULTILINE)
            seen = set()
            all_freqs = []
            for match in matches:
                freq_line = match.group(1)
                freq_values = re.findall(r'([-+]?\d+\.\d+)', freq_line)
                for freq_str in freq_values:
                    try:
                        freq = float(freq_str)
                        if freq not in seen:
                            all_freqs.append(freq)
                            seen.add(freq)
                    except ValueError:
                        continue
            # 如果没有明确区分，将所有频率都归为振动频率（向后兼容）
            if all_freqs:
                vibrations = all_freqs
        
        # 排序频率
        vibrations.sort()
        translations_rotations.sort()
        all_frequencies = vibrations + translations_rotations
        all_frequencies.sort()
        
        return {
            'vibrations': vibrations,
            'translations_rotations': translations_rotations,
            'all': all_frequencies  # 向后兼容
        }

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
            
            # 提取这一步的收敛信息：Force-RMS, Force-Max, Step-RMS, Step-Max
            force_rms = None
            force_max = None
            step_rms = None
            step_max = None
            
            # 查找 "Current values" 行
            current_values_match = re.search(
                r'Current\s+values\s*:\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
                step_content,
                re.IGNORECASE
            )
            if current_values_match:
                try:
                    force_rms = float(current_values_match.group(1))
                    force_max = float(current_values_match.group(2))
                    step_rms = float(current_values_match.group(3))
                    step_max = float(current_values_match.group(4))
                except (ValueError, IndexError):
                    pass
            
            steps.append({
                'step': step_num,
                'energy': energy,
                'scf_energy': None,  # 将从 *.out.tmp 文件中提取
                'gradient': gradient,
                'force_rms': force_rms,
                'force_max': force_max,
                'step_rms': step_rms,
                'step_max': step_max,
            })
        
        opt_info['steps'] = steps
        
        # 检查优化收敛消息（多种格式）
        # 格式1: "Good Job, Geometry Optimization converged in X iterations!"
        good_job_match = re.search(
            r'Good\s+Job[,\s]+Geometry\s+Optimization\s+converged\s+in\s+(\d+)\s+iterations?',
            content,
            re.IGNORECASE
        )
        if good_job_match:
            opt_info['converged'] = True
            try:
                opt_info['iterations'] = int(good_job_match.group(1))
            except (ValueError, IndexError):
                pass
        
        # 格式2: "Total number of iterations: X"
        total_iter_match = re.search(
            r'Total\s+number\s+of\s+iterations:\s*(\d+)',
            content,
            re.IGNORECASE
        )
        if total_iter_match and 'iterations' not in opt_info:
            try:
                opt_info['iterations'] = int(total_iter_match.group(1))
            except (ValueError, IndexError):
                pass
        
        # 提取收敛信息
        # 查找包含收敛检查的更大范围（包括前面的收敛标准）
        converge_section = re.search(
            r'Conv\.\s+tolerance.*?Geom\.\s+converge\s*:.*?(?=\n\n|\n\w|\n\||$)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if converge_section:
            section = converge_section.group(0)
            
            # 检查是否收敛（如果还没检测到）
            if not opt_info.get('converged') and re.search(r'Geom\.\s+converge\s*:.*?Yes', section, re.IGNORECASE):
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
    
    def extract_scf_energies_from_tmp(self, tmp_file: str) -> List[float]:
        """
        从 *.out.tmp 文件中提取每一步优化步骤的 SCF 能量
        
        Args:
            tmp_file: *.out.tmp 文件路径
        
        Returns:
            SCF 能量列表，按优化步骤顺序排列
        """
        scf_energies = []
        tmp_path = Path(tmp_file)
        if not tmp_path.exists():
            return scf_energies
        
        with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 查找所有的 "E_tot = " 行，这些是每次优化步骤的最终 SCF 能量
        # 格式：E_tot =              -114.37036631
        # 注意：*.out.tmp 文件中可能包含多次 SCF 计算，每次优化步骤对应一次
        # 我们需要找到每次 "Final scf result" 后的 E_tot
        
        # 方法1：查找 "Final scf result" 后的 E_tot
        final_scf_pattern = r'Final\s+scf\s+result.*?E_tot\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)'
        matches = re.finditer(final_scf_pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            try:
                energy = float(match.group(1))
                scf_energies.append(energy)
            except (ValueError, IndexError):
                continue
        
        # 如果方法1没有找到，尝试方法2：直接查找所有 E_tot = 行
        # 但需要过滤掉重复的（同一优化步骤可能有多次迭代）
        if not scf_energies:
            e_tot_pattern = r'E_tot\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)'
            matches = list(re.finditer(e_tot_pattern, content, re.IGNORECASE))
            # 只取每个 "Final scf result" 块后的第一个 E_tot
            last_final_pos = -1
            for match in matches:
                # 检查这个 E_tot 是否在 "Final scf result" 之后
                pos = match.start()
                # 向前查找最近的 "Final scf result"
                before_text = content[max(0, pos - 500):pos]
                if re.search(r'Final\s+scf\s+result', before_text, re.IGNORECASE):
                    try:
                        energy = float(match.group(1))
                        # 避免重复（如果能量值相同且位置接近，可能是同一优化步骤）
                        if not scf_energies or abs(energy - scf_energies[-1]) > 1e-6:
                            scf_energies.append(energy)
                    except (ValueError, IndexError):
                        continue
        
        return scf_energies
    
    def extract_final_scf_energy_components(self, tmp_file: str) -> Optional[Dict[str, float]]:
        """
        从 *.out.tmp 文件中提取最后一次 SCF 计算的能量分解信息
        
        Args:
            tmp_file: *.out.tmp 文件路径
        
        Returns:
            包含能量分解信息的字典，如果未找到则返回 None
        """
        tmp_path = Path(tmp_file)
        if not tmp_path.exists():
            return None
        
        with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 查找最后一个 "Final scf result" 块
        final_scf_blocks = list(re.finditer(
            r'Final\s+scf\s+result(.*?)(?=Final\s+scf\s+result|\[Final|$)',
            content,
            re.IGNORECASE | re.DOTALL
        ))
        
        if not final_scf_blocks:
            return None
        
        # 取最后一个块
        last_block = final_scf_blocks[-1].group(1)
        
        components = {}
        
        # 提取各种能量分量
        energy_patterns = {
            'E_tot': r'E_tot\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            'E_ele': r'E_ele\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            'E_sol': r'E_sol\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            'E_nn': r'E_nn\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            'E_1e': r'E_1e\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            'E_ne': r'E_ne\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            'E_kin': r'E_kin\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            'E_ee': r'E_ee\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            'E_xc': r'E_xc\s*=\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            'virial_ratio': r'Virial\s+Ratio\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
        }
        
        for key, pattern in energy_patterns.items():
            match = re.search(pattern, last_block, re.IGNORECASE)
            if match:
                try:
                    components[key] = float(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        return components if components else None
    
    def extract_thermochemistry(self, content: str) -> Optional[Dict[str, Any]]:
        """
        提取热力学数据
        
        Returns:
            包含热力学数据的字典，如果未找到则返回 None
        """
        thermochemistry = {}
        
        # 查找热力学部分
        # 更宽松的匹配模式，因为可能有不同的分隔符
        thermo_section_match = re.search(
            r'Thermal\s+Contributions\s+to\s+Energies.*?(?:Sum\s+of\s+electronic\s+and\s+thermal\s+Free\s+Energies.*?[-+]?\d+\.\d+).*?(?=\n\s*\*\*\*|$|\n\s*\[)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        # 如果没找到，尝试更简单的模式
        if not thermo_section_match:
            thermo_section_match = re.search(
                r'Zero-point\s+Energy.*?Sum\s+of\s+electronic.*?Free\s+Energies.*?[-+]?\d+\.\d+.*?(?=\n\s*===|$)',
                content,
                re.IGNORECASE | re.DOTALL
            )
        
        if not thermo_section_match:
            return None
        
        thermo_section = thermo_section_match.group(0)
        
        # 提取温度
        temp_match = re.search(r'Temperature\s*=\s*([-+]?\d+\.?\d*)\s*Kelvin', thermo_section, re.IGNORECASE)
        if temp_match:
            try:
                thermochemistry['temperature'] = float(temp_match.group(1))
            except (ValueError, IndexError):
                pass
        
        # 提取压力
        press_match = re.search(r'Pressure\s*=\s*([-+]?\d+\.?\d*)\s*Atm', thermo_section, re.IGNORECASE)
        if press_match:
            try:
                thermochemistry['pressure'] = float(press_match.group(1))
            except (ValueError, IndexError):
                pass
        
        # 提取零点能（ZPE）
        zpe_match = re.search(
            r'Zero-point\s+Energy\s*:\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            thermo_section,
            re.IGNORECASE
        )
        if zpe_match:
            try:
                thermochemistry['zero_point_energy'] = {
                    'hartree': float(zpe_match.group(1)),
                    'kcal_per_mol': float(zpe_match.group(2))
                }
            except (ValueError, IndexError):
                pass
        
        # 提取热校正能
        thermal_energy_match = re.search(
            r'Thermal\s+correction\s+to\s+Energy\s*:\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            thermo_section,
            re.IGNORECASE
        )
        if thermal_energy_match:
            try:
                thermochemistry['thermal_correction_energy'] = {
                    'hartree': float(thermal_energy_match.group(1)),
                    'kcal_per_mol': float(thermal_energy_match.group(2))
                }
            except (ValueError, IndexError):
                pass
        
        # 提取热校正焓
        thermal_enthalpy_match = re.search(
            r'Thermal\s+correction\s+to\s+Enthalpy\s*:\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            thermo_section,
            re.IGNORECASE
        )
        if thermal_enthalpy_match:
            try:
                thermochemistry['thermal_correction_enthalpy'] = {
                    'hartree': float(thermal_enthalpy_match.group(1)),
                    'kcal_per_mol': float(thermal_enthalpy_match.group(2))
                }
            except (ValueError, IndexError):
                pass
        
        # 提取热校正 Gibbs 自由能
        thermal_gibbs_match = re.search(
            r'Thermal\s+correction\s+to\s+Gibbs\s+Free\s+Energy\s*:\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)\s+([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            thermo_section,
            re.IGNORECASE
        )
        if thermal_gibbs_match:
            try:
                thermochemistry['thermal_correction_gibbs'] = {
                    'hartree': float(thermal_gibbs_match.group(1)),
                    'kcal_per_mol': float(thermal_gibbs_match.group(2))
                }
            except (ValueError, IndexError):
                pass
        
        # 提取组合能量（电子能 + 各种校正）
        # Sum of electronic and zero-point Energies
        zpe_sum_match = re.search(
            r'Sum\s+of\s+electronic\s+and\s+zero-point\s+Energies\s*:\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            thermo_section,
            re.IGNORECASE
        )
        if zpe_sum_match:
            try:
                thermochemistry['electronic_plus_zpe'] = float(zpe_sum_match.group(1))
            except (ValueError, IndexError):
                pass
        
        # Sum of electronic and thermal Energies
        thermal_sum_match = re.search(
            r'Sum\s+of\s+electronic\s+and\s+thermal\s+Energies\s*:\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            thermo_section,
            re.IGNORECASE
        )
        if thermal_sum_match:
            try:
                thermochemistry['electronic_plus_thermal'] = float(thermal_sum_match.group(1))
            except (ValueError, IndexError):
                pass
        
        # Sum of electronic and thermal Enthalpies
        enthalpy_sum_match = re.search(
            r'Sum\s+of\s+electronic\s+and\s+thermal\s+Enthalpies\s*:\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            thermo_section,
            re.IGNORECASE
        )
        if enthalpy_sum_match:
            try:
                thermochemistry['electronic_plus_enthalpy'] = float(enthalpy_sum_match.group(1))
            except (ValueError, IndexError):
                pass
        
        # Sum of electronic and thermal Free Energies
        gibbs_sum_match = re.search(
            r'Sum\s+of\s+electronic\s+and\s+thermal\s+Free\s+Energies\s*:\s*([-+]?\d+\.?\d*[Ee]?[-+]?\d*)',
            thermo_section,
            re.IGNORECASE
        )
        if gibbs_sum_match:
            try:
                thermochemistry['electronic_plus_gibbs'] = float(gibbs_sum_match.group(1))
            except (ValueError, IndexError):
                pass
        
        return thermochemistry if thermochemistry else None
    
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
    
    def extract_resp_gradient_info(self, content: str) -> Optional[Dict[str, Any]]:
        """
        提取resp模块的激发态梯度计算信息
        
        BDF在计算TDDFT激发态梯度时，会在resp模块输出类似以下标记：
        - "<Now following: Root    1>" 或 "<Now following: Root    N>"
        - "Root    N"
        
        这些标记表示正在计算第N个激发态（能量最低的为Root 1）的梯度。
        由于梯度计算会多次迭代，每个目标激发态的梯度计算可能包含多个这样的标记。
        
        Args:
            content: BDF输出文件内容
            
        Returns:
            包含激发态梯度信息的字典，如果未找到则返回None：
            {
                'target_roots': [1, 2, ...],  # 所有被计算梯度的激发态根号列表
                'root_counts': {1: 18, 2: 5, ...},  # 每个根号出现的次数（迭代次数）
                'primary_root': 1,  # 主要计算的根号（出现次数最多的）
                'description': '...'  # 描述信息
            }
        """
        resp_info = {}
        
        # 匹配 "<Now following: Root    N>" 格式
        pattern1 = r'<Now\s+following:\s*Root\s+(\d+)>'
        matches1 = re.finditer(pattern1, content, re.IGNORECASE)
        
        # 匹配 "Root    N" 格式（独立行）
        pattern2 = r'^\s*Root\s+(\d+)\s*$'
        matches2 = re.finditer(pattern2, content, re.MULTILINE | re.IGNORECASE)
        
        # 收集所有根号
        root_numbers = []
        for match in matches1:
            try:
                root_num = int(match.group(1))
                root_numbers.append(root_num)
            except (ValueError, IndexError):
                continue
        
        for match in matches2:
            try:
                root_num = int(match.group(1))
                root_numbers.append(root_num)
            except (ValueError, IndexError):
                continue
        
        if not root_numbers:
            return None
        
        # 统计每个根号出现的次数
        root_counts = {}
        for root_num in root_numbers:
            root_counts[root_num] = root_counts.get(root_num, 0) + 1
        
        # 获取所有被计算的根号（去重并排序）
        target_roots = sorted(set(root_numbers))
        
        # 确定主要计算的根号（出现次数最多的）
        primary_root = max(root_counts.items(), key=lambda x: x[1])[0] if root_counts else None
        
        resp_info['target_roots'] = target_roots
        resp_info['root_counts'] = root_counts
        resp_info['primary_root'] = primary_root
        resp_info['total_gradient_calculations'] = len(root_numbers)
        
        # 生成描述信息（使用英文，因为会在报告中根据语言转换）
        if primary_root:
            if len(target_roots) == 1:
                resp_info['description'] = (
                    f"Calculated the gradient of TDDFT excited state {primary_root} "
                    f"(the lowest-energy excited state). Performed {root_counts[primary_root]} gradient calculation iterations."
                )
            else:
                root_desc = ", ".join([f"Root {r} ({root_counts[r]} iterations)" for r in target_roots])
                resp_info['description'] = (
                    f"Calculated gradients for multiple TDDFT excited states: {root_desc}. "
                    f"The primary calculation is for excited state {primary_root} "
                    f"(Root {primary_root}, appears {root_counts[primary_root]} times)."
                )
        else:
            resp_info['description'] = f"Calculated gradients for multiple TDDFT excited states: {', '.join([f'Root {r}' for r in target_roots])}."
        
        return resp_info
    
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
        
        # 从简单的格式中提取溶剂信息（如果没有找到详细的溶剂部分）
        # 格式: "solvent\nwater\nsolmodel\nsmd" 或类似格式
        if 'solvent' not in properties or not properties['solvent']:
            # 查找溶剂关键词附近的内容
            solvent_simple_match = re.search(
                r'solvent\s*\n\s*(\w+)',
                content,
                re.IGNORECASE | re.MULTILINE
            )
            if solvent_simple_match:
                properties['solvent'] = properties.get('solvent', {})
                properties['solvent']['solvent'] = solvent_simple_match.group(1).strip()
            
            # 查找溶剂模型
            solmodel_match = re.search(
                r'solmodel\s*\n\s*(\w+)',
                content,
                re.IGNORECASE | re.MULTILINE
            )
            if solmodel_match:
                if 'solvent' not in properties:
                    properties['solvent'] = {}
                properties['solvent']['method'] = solmodel_match.group(1).strip()
            
            # 如果没有找到详细的溶剂部分，但有溶剂相关信息，标记为隐式溶剂
            if 'solvent' in properties and properties['solvent']:
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
    
    def extract_scf_method(self, content: str) -> Optional[Dict[str, Any]]:
        """
        提取SCF计算方法类型
        
        BDF在SCF模块输出中会显示使用的计算方法，如：
        - RHF: 限制性 Hartree-Fock
        - UHF: 非限制性 Hartree-Fock
        - ROHF: 限制性开壳层 Hartree-Fock
        - RKS: 限制性 Kohn-Sham DFT
        - UKS: 非限制性 Kohn-Sham DFT
        - ROKS: 限制性开壳层 Kohn-Sham DFT
        
        通常在SCF迭代开始时会显示方法类型。
        
        Args:
            content: BDF输出文件内容
            
        Returns:
            包含SCF方法信息的字典，如果未找到则返回None：
            {
                'method': 'RHF',  # 方法类型：RHF/UHF/ROHF/RKS/UKS/ROKS
                'is_restricted': True,  # 是否为限制性方法（RHF/RKS/ROHF/ROKS）
                'is_unrestricted': False,  # 是否为非限制性方法（UHF/UKS）
                'is_rohf': False,  # 是否为限制性开壳层方法（ROHF/ROKS）
                'is_dft': False,  # 是否为DFT方法（RKS/UKS/ROKS）
                'is_hf': True,  # 是否为HF方法（RHF/UHF/ROHF）
            }
        """
        scf_method_info = {}
        
        # 查找SCF方法类型
        # 可能在以下位置出现：
        # 1. SCF迭代开始时的输出
        # 2. 输入文件回显（$SCF模块）
        # 3. 方法说明部分
        
        # 方法1：查找SCF迭代输出中的方法标识
        # 格式可能：RHF calculation, UHF calculation等
        method_patterns = [
            (r'\b(RHF)\b', 'RHF'),
            (r'\b(UHF)\b', 'UHF'),
            (r'\b(ROHF)\b', 'ROHF'),
            (r'\b(RKS)\b', 'RKS'),
            (r'\b(UKS)\b', 'UKS'),
            (r'\b(ROKS)\b', 'ROKS'),
        ]
        
        found_method = None
        # 优先从输入文件回显部分查找（更准确）
        # 查找 $SCF ... $end 之间的方法标识
        scf_input_match = re.search(
            r'\$SCF[^\$]*?(?=\$|\n\n|\n\|\||$)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        
        if scf_input_match:
            scf_input_section = scf_input_match.group(0)
            # 在SCF输入部分查找方法标识（通常在$SCF和$end之间）
            for pattern, method_name in method_patterns:
                if re.search(pattern, scf_input_section, re.IGNORECASE):
                    found_method = method_name
                    break
        
        # 如果没找到，再从输出部分查找
        if not found_method:
            for pattern, method_name in method_patterns:
                # 在SCF相关部分查找
                scf_section_match = re.search(
                    r'\$SCF.*?(?=\$|\n\n|\n\|\||$)',
                    content,
                    re.IGNORECASE | re.DOTALL
                )
                
                if scf_section_match:
                    scf_section = scf_section_match.group(0)
                    if re.search(pattern, scf_section, re.IGNORECASE):
                        found_method = method_name
                        break
        
        # 方法2：如果没找到，在整个文件中查找（可能在输出中）
        if not found_method:
            for pattern, method_name in method_patterns:
                # 查找方法名称，但排除一些误匹配（如变量名）
                # 确保是独立的方法标识
                match = re.search(rf'\b{method_name}\b', content, re.IGNORECASE)
                if match:
                    # 检查上下文，确保是SCF方法而不是其他
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end].lower()
                    # 如果上下文包含SCF相关关键词，认为是方法标识
                    if any(keyword in context for keyword in ['scf', 'method', 'calculation', '$scf']):
                        found_method = method_name
                        break
        
        if found_method:
            scf_method_info['method'] = found_method
            
            # 判断方法特性
            scf_method_info['is_restricted'] = found_method in ['RHF', 'RKS', 'ROHF', 'ROKS']
            scf_method_info['is_unrestricted'] = found_method in ['UHF', 'UKS']
            scf_method_info['is_rohf'] = found_method in ['ROHF', 'ROKS']
            scf_method_info['is_dft'] = found_method in ['RKS', 'UKS', 'ROKS']
            scf_method_info['is_hf'] = found_method in ['RHF', 'UHF', 'ROHF']
            
            return scf_method_info
        
        return None
    
    def extract_symmetry_info(self, content: str) -> Optional[Dict[str, Any]]:
        """
        提取对称群信息
        
        BDF在compass输出中会包含以下对称群相关信息：
        - gsym: D06H, noper=   24  (检测到的对称群和操作数)
        - Point group name D(6H)   (BDF自动判断的对称群)
        - User set point group as D(6H)   (用户设定的对称群，由compass中关键词group指定)
        - Largest Abelian Subgroup D(2H)  8  (最大阿贝尔子群)
        - Symmetry check OK  (对称性检查通过)
        
        Args:
            content: BDF输出文件内容
            
        Returns:
            包含对称群信息的字典，如果未找到则返回None：
            {
                'detected_group': 'D(6H)',  # BDF自动检测的对称群
                'user_set_group': 'D(6H)',  # 用户设定的对称群（如果有）
                'largest_abelian_subgroup': 'D(2H)',  # 最大阿贝尔子群（如果有）
                'noper': 24,  # 对称操作数
                'abelian_subgroup_noper': 8,  # 阿贝尔子群的操作数（如果有）
                'symmetry_check': 'OK',  # 对称性检查结果
                'is_subgroup': True/False,  # 用户设定的群是否是检测到的群的子群
            }
        """
        symmetry_info = {}
        
        # 提取 gsym 和 noper
        # 格式：gsym: D06H, noper=   24
        gsym_match = re.search(r'gsym:\s*([^\s,]+)', content, re.IGNORECASE)
        if gsym_match:
            # 将格式从 D06H 转换为 D(6H)
            gsym_raw = gsym_match.group(1).strip()
            # 处理格式转换：D06H -> D(6H), C2V -> C(2V), D2H -> D(2H)
            # 匹配数字后跟字母的模式
            gsym_normalized = self._normalize_point_group_format(gsym_raw)
            symmetry_info['detected_group_raw'] = gsym_raw
            symmetry_info['detected_group'] = gsym_normalized
        
        noper_match = re.search(r'noper\s*=\s*(\d+)', content, re.IGNORECASE)
        if noper_match:
            try:
                symmetry_info['noper'] = int(noper_match.group(1))
            except (ValueError, IndexError):
                pass
        
        # 提取 Point group name（BDF自动判断的对称群）
        # 格式：Point group name D(6H)   
        point_group_match = re.search(r'Point\s+group\s+name\s+([^\s]+)', content, re.IGNORECASE)
        if point_group_match:
            point_group = point_group_match.group(1).strip()
            symmetry_info['detected_group'] = point_group
        
        # 提取 User set point group（用户设定的对称群）
        # 格式：User set point group as D(6H)   
        user_group_match = re.search(r'User\s+set\s+point\s+group\s+as\s+([^\s]+)', content, re.IGNORECASE)
        if user_group_match:
            user_group = user_group_match.group(1).strip()
            symmetry_info['user_set_group'] = user_group
            
            # 判断用户设定的群是否是检测到的群的子群
            if 'detected_group' in symmetry_info:
                detected = symmetry_info['detected_group']
                # 简单判断：如果用户设定的群和检测到的群相同，或者是其子群
                # 这里可以做更复杂的子群判断，但通常BDF会检查并报错如果不是子群
                symmetry_info['is_subgroup'] = (user_group == detected or 
                                                self._is_likely_subgroup(user_group, detected))
        
        # 提取 Largest Abelian Subgroup（最大阿贝尔子群）
        # 格式：Largest Abelian Subgroup D(2H)                       8
        abelian_match = re.search(r'Largest\s+Abelian\s+Subgroup\s+([^\s]+)\s+(\d+)', content, re.IGNORECASE)
        if abelian_match:
            abelian_group = abelian_match.group(1).strip()
            abelian_noper = abelian_match.group(2).strip()
            symmetry_info['largest_abelian_subgroup'] = abelian_group
            try:
                symmetry_info['abelian_subgroup_noper'] = int(abelian_noper)
            except (ValueError, IndexError):
                pass
        
        # 提取 Symmetry check 结果
        # 格式：Symmetry check OK
        symmetry_check_match = re.search(r'Symmetry\s+check\s+(\w+)', content, re.IGNORECASE)
        if symmetry_check_match:
            symmetry_info['symmetry_check'] = symmetry_check_match.group(1).strip()
        
        return symmetry_info if symmetry_info else None
    
    def extract_irrep_info(self, content: str) -> Optional[Dict[str, Any]]:
        """
        提取不可约表示（Irrep）和分子轨道信息
        
        BDF在compass输出中会包含以下信息（新格式，三行在一起）：
        - Total number of basis functions:     114     114  (总基函数数目)
        - Number of irreps:   8  (不可约表示数目)
        - Irrep :   Ag        B1g       B2g       B3g       Au        B1u       B2u       B3u  (不可约表示标记，同一行)
        - Norb  :     24        18         9         6         6         9        18        24  (每个不可约表示的轨道数，同一行)
        
        Args:
            content: BDF输出文件内容
            
        Returns:
            包含不可约表示信息的字典，如果未找到则返回None：
            {
                'total_basis_functions': 114,  # 总基函数数目
                'number_of_irreps': 8,  # 不可约表示数目
                'irreps': [  # 不可约表示列表
                    {
                        'irrep': 'Ag',  # 不可约表示标记
                        'norb': 24,  # 该不可约表示的分子轨道数目
                    },
                    ...
                ],
                'total_orbitals': 114,  # 总分子轨道数（所有不可约表示之和）
            }
        """
        irrep_info = {}
        
        # 提取总基函数数目
        # 格式：Total number of basis functions:     114     114
        # 注意：可能有两个数字，第一个是alpha，第二个是beta（对于开壳层）
        total_basis_match = re.search(
            r'Total\s+number\s+of\s+basis\s+functions:\s+(\d+)(?:\s+(\d+))?',
            content,
            re.IGNORECASE
        )
        if total_basis_match:
            try:
                alpha_basis = int(total_basis_match.group(1))
                beta_basis = int(total_basis_match.group(2)) if total_basis_match.group(2) else None
                irrep_info['total_basis_functions'] = alpha_basis
                if beta_basis is not None:
                    irrep_info['total_basis_functions_beta'] = beta_basis
            except (ValueError, IndexError):
                pass
        
        # 提取不可约表示数目
        # 格式：Number of irreps:   8
        num_irreps_match = re.search(
            r'Number\s+of\s+irreps:\s*(\d+)',
            content,
            re.IGNORECASE
        )
        if num_irreps_match:
            try:
                irrep_info['number_of_irreps'] = int(num_irreps_match.group(1))
            except (ValueError, IndexError):
                pass
        
        # 提取不可约表示和轨道数（新格式：三行在一起）
        # 格式：
        #   Number of irreps:   8
        #   Irrep :   Ag        B1g       B2g       B3g       Au        B1u       B2u       B3u
        #   Norb  :     24        18         9         6         6         9        18        24
        
        lines = content.split('\n')
        irreps = []
        
        # 查找包含这三行的区域
        for i, line in enumerate(lines):
            # 查找 "Irrep :" 行（包含所有不可约表示标记）
            irrep_line_match = re.search(r'Irrep\s*:\s*(.+)', line, re.IGNORECASE)
            if irrep_line_match:
                # 提取这一行中的所有不可约表示标记
                irrep_line = irrep_line_match.group(1).strip()
                # 不可约表示标记通常格式：字母+可选数字+可选字母（如 Ag, B1g, B2g, B3g, Au, B1u, B2u, B3u）
                # 使用正则表达式提取所有不可约表示标记
                irrep_pattern = r'\b([A-Z][0-9]?[a-z]?[0-9]?[a-z]?)\b'
                irrep_labels = re.findall(irrep_pattern, irrep_line)
                # 过滤：只保留看起来像不可约表示标记的（长度通常1-5个字符，排除常见英文单词）
                irrep_labels = [irrep for irrep in irrep_labels 
                               if 1 <= len(irrep) <= 5 
                               and not irrep.lower() in ['for', 'iden', 'irep', 'norb', 'irrep']]
                
                # 查找下一行的 "Norb :" 行（包含所有轨道数）
                if i + 1 < len(lines):
                    norb_line = lines[i + 1]
                    norb_line_match = re.search(r'Norb\s*:\s*(.+)', norb_line, re.IGNORECASE)
                    if norb_line_match:
                        norb_line_content = norb_line_match.group(1).strip()
                        # 提取所有数字（轨道数）
                        norb_values = re.findall(r'(\d+)', norb_line_content)
                        norb_values = [int(val) for val in norb_values]
                        
                        # 匹配不可约表示和轨道数
                        if len(irrep_labels) == len(norb_values):
                            for irrep_label, norb_value in zip(irrep_labels, norb_values):
                                irreps.append({
                                    'irrep': irrep_label,
                                    'norb': norb_value
                                })
                            break  # 找到后退出循环
        
        # 如果新格式没找到，尝试旧格式（向后兼容）
        if not irreps:
            # 旧格式：每个不可约表示单独列出
            #   Irrep :     A
            #   Norb  :     22
            current_irrep = None
            for i, line in enumerate(lines):
                # 匹配 "Irrep :     A" 格式
                irrep_match = re.search(r'Irrep\s*:\s*([A-Z0-9]+)', line, re.IGNORECASE)
                if irrep_match:
                    current_irrep = irrep_match.group(1).strip()
                
                # 匹配 "Norb  :     22" 格式
                norb_match = re.search(r'Norb\s*:\s*(\d+)', line, re.IGNORECASE)
                if norb_match and current_irrep:
                    try:
                        norb_value = int(norb_match.group(1))
                        # 检查是否已经存在
                        existing = next((ir for ir in irreps if ir.get('irrep') == current_irrep), None)
                        if not existing:
                            irreps.append({
                                'irrep': current_irrep,
                                'norb': norb_value
                            })
                        current_irrep = None
                    except (ValueError, IndexError):
                        pass
        
        # 如果找到了不可约表示，添加到结果中
        if irreps:
            irrep_info['irreps'] = irreps
            # 计算总轨道数
            total_orbitals = sum(ir['norb'] for ir in irreps)
            irrep_info['total_orbitals'] = total_orbitals
        
        return irrep_info if irrep_info else None
    
    def extract_occupation_info(self, content: str, scf_method: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        提取SCF计算分子轨道占据信息
        
        BDF在SCF模块输出中会包含以下信息：
        [Final occupation pattern: ]
        Irreps:        Ag      B1g     B2g     B3g     Au      B1u     B2u     B3u 
        detailed occupation for iden/irep:      1   1
        1.00 1.00 1.00 1.00 1.00 1.00 0.00 0.00 0.00 0.00
        ...
        Alpha       6.00    3.00    1.00    1.00    0.00    1.00    4.00    5.00
        Beta        6.00    3.00    1.00    1.00    0.00    1.00    4.00    5.00  (对于UHF/UKS)
        
        对于RHF/RKS/ROHF/ROKS计算，alpha和beta轨道占据数相同，所以只输出alpha轨道占据数。
        对于UHF/UKS计算，会分别输出alpha和beta轨道占据数。
        
        Args:
            content: BDF输出文件内容
            scf_method: 已解析的SCF方法信息（可选），用于判断是否为限制性方法
            
        Returns:
            包含轨道占据信息的字典，如果未找到则返回None：
            {
                'irreps': ['Ag', 'B1g', 'B2g', ...],  # 不可约表示标记列表
                'alpha_occupation': [6.00, 3.00, 1.00, ...],  # Alpha轨道占据数（每个不可约表示）
                'beta_occupation': [6.00, 3.00, 1.00, ...],  # Beta轨道占据数（RHF/RKS与alpha相同）
                'total_alpha_electrons': 21.00,  # Alpha电子总数
                'total_beta_electrons': 21.00,  # Beta电子总数
                'total_electrons': 42.00,  # 总电子数
                'is_rhf_rks': True,  # 是否为RHF/RKS计算（alpha=beta）
                'ground_state_irrep': 'Ag',  # 基态波函数的对称性（第一个不可约表示，全对称表示）
            }
        """
        occupation_info = {}
        
        # 查找 [Final occupation pattern: ] 部分
        pattern_section = re.search(
            r'\[Final\s+occupation\s+pattern:\s*\]',
            content,
            re.IGNORECASE
        )
        
        if not pattern_section:
            return None
        
        # 从pattern_section开始提取后续内容（限制在合理范围内，比如5000字符）
        start_pos = pattern_section.end()
        section_content = content[start_pos:start_pos + 5000]
        
        # 提取不可约表示标记行
        # 格式：Irreps:        Ag      B1g     B2g     B3g     Au      B1u     B2u     B3u
        # 注意：不可约表示标记通常包含字母和数字，如 A, A1, B1g, E1u等
        # 需要匹配到下一行开始之前（通常是"detailed occupation"或"Alpha"行）
        irrep_line_match = re.search(
            r'Irreps:\s+([A-Z0-9\s]+?)(?=\n\s*(?:detailed|Alpha|Beta|\n))',
            section_content,
            re.IGNORECASE | re.MULTILINE
        )
        
        irreps = []
        if irrep_line_match:
            irrep_line = irrep_line_match.group(1)
            # 提取所有不可约表示标记
            # 不可约表示标记通常格式：字母+可选数字+可选字母（如 A, A1, B1g, E1u, A1G等）
            # 排除常见英文单词
            irrep_pattern = r'\b([A-Z][0-9]?[a-z]?[0-9]?[a-z]?)\b'
            irrep_matches = re.findall(irrep_pattern, irrep_line)
            # 进一步过滤：只保留看起来像不可约表示标记的（长度通常1-5个字符）
            irreps = [irrep for irrep in irrep_matches if 1 <= len(irrep) <= 5 and not irrep.lower() in ['for', 'iden', 'irep']]
            occupation_info['irreps'] = irreps
        
        # 提取Alpha轨道占据数
        # 格式：Alpha       6.00    3.00    1.00    1.00    0.00    1.00    4.00    5.00
        alpha_match = re.search(
            r'Alpha\s+([\d.\s]+)',
            section_content,
            re.IGNORECASE
        )
        
        alpha_occupation = []
        if alpha_match:
            alpha_line = alpha_match.group(1)
            # 提取所有数字
            alpha_values = re.findall(r'(\d+\.\d+)', alpha_line)
            alpha_occupation = [float(val) for val in alpha_values]
            occupation_info['alpha_occupation'] = alpha_occupation
        
        # 提取Beta轨道占据数（如果有）
        # 格式：Beta        6.00    3.00    1.00    1.00    0.00    1.00    4.00    5.00
        beta_match = re.search(
            r'Beta\s+([\d.\s]+)',
            section_content,
            re.IGNORECASE
        )
        
        beta_occupation = []
        if beta_match:
            beta_line = beta_match.group(1)
            beta_values = re.findall(r'(\d+\.\d+)', beta_line)
            beta_occupation = [float(val) for val in beta_values]
            occupation_info['beta_occupation'] = beta_occupation
        else:
            # 判断是否为限制性方法（RHF/RKS/ROHF/ROKS）
            # 优先使用传入的SCF方法信息
            is_restricted = False
            method_name = None
            
            if scf_method and 'method' in scf_method:
                method_name = scf_method['method']
                is_restricted = scf_method.get('is_restricted', False)
            else:
                # 从content中查找SCF方法标识
                scf_method_match = re.search(r'\b(RHF|RKS|ROHF|ROKS|UHF|UKS)\b', content, re.IGNORECASE)
                if scf_method_match:
                    method_name = scf_method_match.group(1).upper()
                    is_restricted = method_name in ['RHF', 'RKS', 'ROHF', 'ROKS']
            
            # 对于限制性方法（RHF/RKS/ROHF/ROKS），beta占据数等于alpha占据数
            if is_restricted and alpha_occupation:
                beta_occupation = alpha_occupation.copy()
                occupation_info['beta_occupation'] = beta_occupation
                occupation_info['is_restricted'] = True
                # 判断具体类型
                if method_name:
                    if method_name in ['RHF', 'RKS']:
                        occupation_info['is_rhf_rks'] = True
                    elif method_name in ['ROHF', 'ROKS']:
                        occupation_info['is_rohf_roks'] = True
                else:
                    # 默认假设是RHF/RKS
                    occupation_info['is_rhf_rks'] = True
            elif not is_restricted:
                # 非限制性方法（UHF/UKS），但没有找到Beta占据数
                # 这可能表示输出不完整，记录警告
                occupation_info['warning'] = "非限制性方法（UHF/UKS）但未找到Beta轨道占据数"
        
        # 计算总电子数
        if alpha_occupation:
            total_alpha = sum(alpha_occupation)
            occupation_info['total_alpha_electrons'] = total_alpha
        
        if beta_occupation:
            total_beta = sum(beta_occupation)
            occupation_info['total_beta_electrons'] = total_beta
        
        if alpha_occupation and beta_occupation:
            total_electrons = sum(alpha_occupation) + sum(beta_occupation)
            occupation_info['total_electrons'] = total_electrons
        
        # 基态波函数的对称性：第一个不可约表示（全对称表示）
        if irreps:
            occupation_info['ground_state_irrep'] = irreps[0]
        
        # 验证：不可约表示数量应该与占据数数量一致
        if irreps and alpha_occupation:
            if len(irreps) != len(alpha_occupation):
                # 如果不一致，记录警告但不失败
                occupation_info['warning'] = f"不可约表示数量({len(irreps)})与占据数数量({len(alpha_occupation)})不一致"
        
        return occupation_info if occupation_info else None
    
    def extract_scf_state_symmetry(self, content: str) -> Optional[Dict[str, Any]]:
        """
        提取SCF State symmetry（SCF计算的Slater行列式对称性）
        
        BDF在SCF输出中会包含以下信息：
        SCF State symmetry : Ag
        
        这给出了SCF计算的Slater行列式对称性的不可约表示标记。
        对于闭壳层电子态，这通常与基态波函数的对称性（第一个不可约表示，全对称表示）相同。
        
        Args:
            content: BDF输出文件内容
            
        Returns:
            包含SCF State symmetry信息的字典，如果未找到则返回None：
            {
                'irrep': 'Ag',  # 不可约表示标记
                'description': 'SCF计算的Slater行列式对称性',
            }
        """
        symmetry_info = {}
        
        # 查找SCF State symmetry
        # 格式：SCF State symmetry : Ag
        pattern = r'SCF\s+State\s+symmetry\s*:\s*([A-Z0-9]+)'
        match = re.search(pattern, content, re.IGNORECASE)
        
        if match:
            irrep = match.group(1).strip()
            symmetry_info['irrep'] = irrep
            symmetry_info['description'] = 'SCF计算的Slater行列式对称性'
            return symmetry_info
        
        return None
    
    def _normalize_point_group_format(self, group: str) -> str:
        """
        将点群格式从 D06H 转换为 D(6H) 格式
        
        Args:
            group: 原始点群字符串，如 "D06H", "C2V", "D2H"
            
        Returns:
            标准化后的点群字符串，如 "D(6H)", "C(2V)", "D(2H)"
        """
        # 如果已经是标准格式（包含括号），直接返回
        if '(' in group and ')' in group:
            return group
        
        # 匹配模式：字母 + 数字 + 字母（如 D06H, C2V, D2H）
        # 或者：字母 + 数字（如 C2, D3）
        pattern = r'^([A-Za-z]+)(\d+)([A-Za-z]*)$'
        match = re.match(pattern, group)
        
        if match:
            prefix = match.group(1)  # D, C, etc.
            number = match.group(2)  # 06, 2, etc.
            suffix = match.group(3)  # H, V, etc.
            
            # 移除前导零
            number = str(int(number))
            
            if suffix:
                return f"{prefix}({number}{suffix})"
            else:
                return f"{prefix}({number})"
        
        # 如果不匹配，返回原字符串
        return group
    
    def _is_likely_subgroup(self, subgroup: str, parent_group: str) -> bool:
        """
        简单判断 subgroup 是否是 parent_group 的子群
        
        这是一个简化的判断，主要用于常见情况。
        完整的子群判断需要群论知识，这里只做基本检查。
        
        Args:
            subgroup: 可能的子群，如 "D(2H)"
            parent_group: 父群，如 "D(6H)"
            
        Returns:
            True 如果可能是子群，False 否则
        """
        # 如果相同，肯定是子群（也是父群本身）
        if subgroup == parent_group:
            return True
        
        # 提取群的基本信息
        def extract_group_info(group_str):
            # 移除括号
            clean = group_str.replace('(', '').replace(')', '')
            # 提取字母前缀和数字
            match = re.match(r'^([A-Za-z]+)(\d+)([A-Za-z]*)$', clean)
            if match:
                return {
                    'prefix': match.group(1),
                    'number': int(match.group(2)) if match.group(2) else None,
                    'suffix': match.group(3) if match.group(3) else ''
                }
            return None
        
        sub_info = extract_group_info(subgroup)
        parent_info = extract_group_info(parent_group)
        
        if not sub_info or not parent_info:
            return False
        
        # 如果前缀不同，通常不是子群（特殊情况除外）
        if sub_info['prefix'] != parent_info['prefix']:
            # 特殊情况：C(2V) 可能是 D(2H) 的子群等，这里简化处理
            return False
        
        # 如果数字相同但后缀不同，可能是子群（如 D(2) 是 D(2H) 的子群）
        if sub_info['number'] == parent_info['number']:
            # 如果子群没有后缀或后缀更少，可能是子群
            if not sub_info['suffix'] or len(sub_info['suffix']) < len(parent_info['suffix']):
                return True
        
        # 如果子群的数字是父群数字的因子，可能是子群
        # 例如：D(2) 可能是 D(6) 的子群（2 是 6 的因子）
        if sub_info['number'] and parent_info['number']:
            if parent_info['number'] % sub_info['number'] == 0:
                return True
        
        return False

