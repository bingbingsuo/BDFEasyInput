"""
Analysis Report Generator

This module provides functionality to generate analysis reports in various formats.
"""

from typing import Dict, Any, Optional

try:
    from typing import Literal
    Language = Literal["zh", "en"]
except ImportError:
    Language = str  # Python 3.7 compatibility

from datetime import datetime
from pathlib import Path
from .report_labels import get_label, get_separator


class AnalysisReportGenerator:
    """分析报告生成器 / Analysis Report Generator"""
    
    def __init__(self, format: str = "markdown", language: Language = "zh"):
        """
        初始化报告生成器
        
        Args:
            format: 报告格式，支持 'markdown', 'html', 'text'
            language: 报告语言，'zh' 表示中文，'en' 表示英文
        """
        self.format = format.lower()
        if self.format not in ['markdown', 'html', 'text']:
            raise ValueError(f"Unsupported format: {format}. Supported: markdown, html, text")
        self.language = language.lower() if language else "zh"
    
    def generate(
        self,
        analysis_result: Dict[str, Any],
        parsed_data: Optional[Dict[str, Any]] = None,
        output_file: Optional[str] = None
    ) -> str:
        """
        生成分析报告
        
        Args:
            analysis_result: AI 分析结果
            parsed_data: 解析后的原始数据（可选）
            output_file: 输出文件路径（可选）
        
        Returns:
            报告内容字符串
        """
        if self.format == 'markdown':
            report = self._generate_markdown(analysis_result, parsed_data, self.language)
        elif self.format == 'html':
            report = self._generate_html(analysis_result, parsed_data, self.language)
        else:
            report = self._generate_text(analysis_result, parsed_data, self.language)
        
        # 如果指定了输出文件，写入文件
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report
    
    
    def _generate_markdown(
        self,
        analysis_result: Dict[str, Any],
        parsed_data: Optional[Dict[str, Any]] = None,
        language: Language = "zh"
    ) -> str:
        """生成 Markdown 格式报告"""
        lines = []
        
        sep = get_separator(language)
        
        # 标题
        title = get_label("report_title", language)
        time_label = get_label("generated_time", language)
        
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"**{time_label}**{sep} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 计算总结
        summary = analysis_result.get('summary', '')
        if summary:
            summary_title = get_label("calculation_summary", language)
            lines.append(f"## {summary_title}")
            lines.append("")
            lines.append(summary)
            lines.append("")
        
        # 能量分析
        energy_analysis = analysis_result.get('energy_analysis', '')
        if energy_analysis:
            energy_title = get_label("energy_analysis", language)
            lines.append(f"## {energy_title}")
            lines.append("")
            lines.append(energy_analysis)
            lines.append("")
        
        # 几何结构分析
        geometry_analysis = analysis_result.get('geometry_analysis', '')
        if geometry_analysis:
            geometry_title = get_label("geometry_analysis", language)
            lines.append(f"## {geometry_title}")
            lines.append("")
            lines.append(geometry_analysis)
            lines.append("")
        
        # 收敛性分析
        convergence_analysis = analysis_result.get('convergence_analysis', '')
        if convergence_analysis:
            convergence_title = get_label("convergence_analysis", language)
            lines.append(f"## {convergence_title}")
            lines.append("")
            lines.append(convergence_analysis)
            lines.append("")
        
        # 原始数据（如果提供）
        if parsed_data:
            raw_data_title = get_label("raw_data", language)
            lines.append(f"## {raw_data_title}")
            lines.append("")
            
            # 几何结构信息 - 最先显示
            geometry = parsed_data.get('geometry', [])
            if geometry:
                geometry_title = get_label("geometry", language)
                lines.append(f"### {geometry_title}")
                lines.append("")
                
                # 检测单位
                units = geometry[0].get('units', 'bohr').lower() if geometry else 'bohr'
                if units == 'bohr':
                    if language == "en":
                        unit_label = "Bohr (atomic units, 1 Bohr ≈ 0.529177 Å)"
                    else:
                        unit_label = "Bohr（原子单位，1 Bohr ≈ 0.529177 Å）"
                elif units == 'angstrom' or units == 'ang':
                    if language == "en":
                        unit_label = "Angstrom (Å)"
                    else:
                        unit_label = "Angstrom（Å）"
                else:
                    unit_label = units
                
                coord_unit_label = get_label("coordinate_units", language)
                atomic_coords_label = get_label("atomic_coordinates", language)
                note_label = get_label("note", language)
                atom_label = get_label("atom", language)
                
                lines.append(f"**{coord_unit_label}**{sep} {unit_label}")
                lines.append("")
                lines.append(f"**{atomic_coords_label}**{sep}")
                lines.append("")
                lines.append(f"| {atom_label} | X | Y | Z |")
                lines.append("|------|---|-----|-----|")
                for atom in geometry:
                    element = atom.get('element', '?')
                    x = atom.get('x', 0.0)
                    y = atom.get('y', 0.0)
                    z = atom.get('z', 0.0)
                    lines.append(f"| {element} | {x:.6f} | {y:.6f} | {z:.6f} |")
                lines.append("")
                lines.append(f"**{note_label}**{sep}")
                lines.append(f"- {get_label('coord_from_bdf', language)}")
                lines.append(f"- {get_label('units_bohr', language)}")
                lines.append(f"- {get_label('bohr_conversion', language)}")
            lines.append("")
            
            energy = parsed_data.get('energy')
            if energy is not None:
                total_energy_label = get_label("total_energy", language)
                lines.append(f"- **{total_energy_label} (E_tot)**{sep} {energy:.10f} Hartree")
            
            scf_energy = parsed_data.get('scf_energy')
            if scf_energy is not None and scf_energy != energy:
                scf_energy_label = get_label("scf_energy", language)
                lines.append(f"- **{scf_energy_label}**{sep} {scf_energy:.10f} Hartree")
            
            converged = parsed_data.get('converged', False)
            convergence_status_label = get_label("convergence_status", language)
            converged_text = get_label("converged", language) if converged else get_label("not_converged", language)
            lines.append(f"- **{convergence_status_label}**{sep} {converged_text}")
            
            # SCF 能量分量详细说明
            properties = parsed_data.get('properties', {})
            
            # HOMO-LUMO gap 信息
            homo_lumo_gap = properties.get('homo_lumo_gap')
            homo_alpha = properties.get('homo_alpha')
            lumo_alpha = properties.get('lumo_alpha')
            homo_beta = properties.get('homo_beta')
            lumo_beta = properties.get('lumo_beta')
            
            if homo_lumo_gap or homo_alpha or lumo_alpha or homo_beta or lumo_beta:
                lines.append("")
                homo_lumo_title = get_label("homo_lumo_orbital_energies", language)
                lines.append(f"### {homo_lumo_title}")
                lines.append("")
                
                if homo_alpha or lumo_alpha:
                    alpha_label = get_label("alpha_orbitals", language)
                    lines.append(f"**{alpha_label}**{sep}")
                    if homo_alpha:
                        homo_label = get_label("homo", language)
                        lines.append(f"- **{homo_label}**{sep} {homo_alpha['au']:.6f} au ({homo_alpha['ev']:.4f} eV)")
                    if lumo_alpha:
                        lumo_label = get_label("lumo", language)
                        lines.append(f"- **{lumo_label}**{sep} {lumo_alpha['au']:.6f} au ({lumo_alpha['ev']:.4f} eV)")
                    lines.append("")
                
                if homo_beta or lumo_beta:
                    beta_label = get_label("beta_orbitals", language)
                    lines.append(f"**{beta_label}**{sep}")
                    if homo_beta:
                        homo_label = get_label("homo", language)
                        lines.append(f"- **{homo_label}**{sep} {homo_beta['au']:.6f} au ({homo_beta['ev']:.4f} eV)")
                    if lumo_beta:
                        lumo_label = get_label("lumo", language)
                        lines.append(f"- **{lumo_label}**{sep} {lumo_beta['au']:.6f} au ({lumo_beta['ev']:.4f} eV)")
                    lines.append("")
                
                if homo_lumo_gap:
                    gap_au = homo_lumo_gap.get('au')
                    gap_ev = homo_lumo_gap.get('ev')
                    gap_label = get_label("homo_lumo_gap", language)
                    lines.append(f"**{gap_label}**{sep} {gap_au:.6f} au ({gap_ev:.4f} eV)")
                    lines.append("")
                    
                    # 根据 gap 值给出建议
                    if gap_ev is not None:
                        if gap_ev < 0.5:
                            warning_label = get_label("warning_small_gap", language)
                            gap_warning = get_label("homo_lumo_gap_very_small", language)
                            lines.append(f"⚠️ **{warning_label}**{sep} {gap_warning}")
                            lines.append("")
                            suggestions_label = get_label("improvement_suggestions", language)
                            lines.append(f"**{suggestions_label}**{sep}")
                            lines.append(f"- {get_label('add_vshift_keyword', language)}")
                            lines.append(f"- {get_label('vshift_example', language)}")
                            lines.append(f"- {get_label('helps_convergence', language)}")
                            lines.append("")
                        elif gap_ev < 1.0:
                            note_label = get_label("note_small_gap", language)
                            gap_note = get_label("homo_lumo_gap_small", language)
                            lines.append(f"⚠️ **{note_label}**{sep} {gap_note}")
                            lines.append(f"- {get_label('add_vshift_keyword', language)}")
                            lines.append("")
                        else:
                            gap_normal = get_label("homo_lumo_gap_normal", language)
                            lines.append(f"✓ {gap_normal}")
                            lines.append("")
            if properties:
                lines.append("")
                scf_energy_title = get_label("scf_energy_components", language)
                lines.append(f"### {scf_energy_title}")
                lines.append("")
                
                # E_tot, E_ele, E_nn
                e_tot = properties.get('E_tot') or energy
                e_ele = properties.get('E_ele')
                e_nn = properties.get('E_nn')
                
                if e_tot is not None:
                    total_energy_rel_title = get_label("total_energy_relation", language)
                    lines.append(f"#### {total_energy_rel_title}")
                    lines.append("")
                    relation_label = get_label("relation", language)
                    lines.append(f"- **E_tot**{sep} {get_label('e_tot_desc', language)}")
                    lines.append(f"- **E_ele**{sep} {get_label('e_ele_desc', language)}")
                    lines.append(f"- **E_nn**{sep} {get_label('e_nn_desc', language)}")
                    lines.append(f"- **{relation_label}**{sep} E_tot = E_ele + E_nn")
                    lines.append("")
                    if e_ele is not None:
                        lines.append(f"  - E_ele = {e_ele:.10f} Hartree")
                    if e_nn is not None:
                        lines.append(f"  - E_nn = {e_nn:.10f} Hartree")
                    if e_tot is not None:
                        lines.append(f"  - E_tot = {e_tot:.10f} Hartree")
                    if e_ele is not None and e_nn is not None:
                        calculated_tot = e_ele + e_nn
                        verify_label = get_label("verify", language)
                        diff_label = get_label("difference", language)
                        if language == "en":
                            diff_text = f"({diff_label}: {abs(calculated_tot - (e_tot or 0)):.2e})"
                        else:
                            diff_text = f"({diff_label}: {abs(calculated_tot - (e_tot or 0)):.2e})"
                        lines.append(f"  - {verify_label}{sep} E_ele + E_nn = {calculated_tot:.10f} Hartree {diff_text}")
                    lines.append("")
                
                # E_1e, E_ne, E_kin
                e_1e = properties.get('E_1e')
                e_ne = properties.get('E_ne')
                e_kin = properties.get('E_kin')
                
                if e_1e is not None or e_ne is not None or e_kin is not None:
                    one_electron_title = get_label("one_electron_energy", language)
                    lines.append(f"#### {one_electron_title}")
                    lines.append("")
                    relation_label = get_label("relation", language)
                    lines.append(f"- **E_1e**{sep} {get_label('e_1e_desc', language)}")
                    lines.append(f"- **E_ne**{sep} {get_label('e_ne_desc', language)}")
                    lines.append(f"- **E_kin**{sep} {get_label('e_kin_desc', language)}")
                    lines.append(f"- **{relation_label}**{sep} E_1e = E_ne + E_kin")
                    lines.append("")
                    if e_ne is not None:
                        lines.append(f"  - E_ne = {e_ne:.10f} Hartree")
                    if e_kin is not None:
                        lines.append(f"  - E_kin = {e_kin:.10f} Hartree")
                    if e_1e is not None:
                        lines.append(f"  - E_1e = {e_1e:.10f} Hartree")
                    if e_ne is not None and e_kin is not None:
                        calculated_1e = e_ne + e_kin
                        verify_label = get_label("verify", language)
                        diff_label = get_label("difference", language)
                        diff_val = abs(calculated_1e - (e_1e or 0))
                        if language == "en":
                            diff_text = f"({diff_label}: {diff_val:.2e})"
                        else:
                            diff_text = f"({diff_label}: {diff_val:.2e})"
                        lines.append(f"  - {verify_label}{sep} E_ne + E_kin = {calculated_1e:.10f} Hartree {diff_text}")
                    lines.append("")
                
                # E_ee, E_xc
                e_ee = properties.get('E_ee')
                e_xc = properties.get('E_xc')
                
                if e_ee is not None or e_xc is not None:
                    two_electron_title = get_label("two_electron_and_xc", language)
                    lines.append(f"#### {two_electron_title}")
                    lines.append("")
                    if e_ee is not None:
                        lines.append(f"- **E_ee**{sep} {get_label('e_ee_desc', language)} = {e_ee:.10f} Hartree")
                        lines.append(f"  - {get_label('includes_coulomb_and_exchange', language)}")
                    if e_xc is not None:
                        lines.append(f"- **E_xc**{sep} {get_label('e_xc_desc', language)} = {e_xc:.10f} Hartree")
                        lines.append(f"  - {get_label('from_dft_calculation', language)}")
                    lines.append("")
                
                # Virial Ratio
                virial_ratio = properties.get('virial_ratio')
                if virial_ratio is not None:
                    virial_title = get_label("virial_ratio", language)
                    lines.append(f"#### {virial_title}")
                    lines.append("")
                    lines.append(f"- **Virial Ratio** = {virial_ratio:.6f}")
                    lines.append(f"  - {get_label('virial_ratio_desc', language)}")
                    if abs(virial_ratio - 2.0) < 0.01:
                        lines.append(f"  - ✓ {get_label('good_quality', language)}")
                    else:
                        diff = abs(virial_ratio - 2.0)
                        poor_quality = get_label("poor_quality", language)
                        may_need_check = get_label("may_need_check", language)
                        lines.append(f"  - ⚠️ {poor_quality} ({diff:.4f}), {may_need_check}")
                    lines.append("")
                
                # SCF 收敛标准
                thresh_ene = properties.get('scf_conv_thresh_ene')
                thresh_den = properties.get('scf_conv_thresh_den')
                final_deltae = properties.get('final_deltae')
                final_deltad = properties.get('final_deltad')
                scf_iterations = properties.get('scf_iterations')
                scf_iter_when_diis_closed = properties.get('scf_iter_when_diis_closed')
                
                if thresh_ene is not None or thresh_den is not None or final_deltae is not None or final_deltad is not None or scf_iterations is not None:
                    scf_conv_title = get_label("scf_convergence_criteria", language)
                    lines.append(f"#### {scf_conv_title}")
                    lines.append("")
                    
                    # SCF 迭代次数
                    if scf_iterations is not None:
                        iter_info_label = get_label("scf_iteration_info", language)
                        iter_count_label = get_label("scf_iterations", language)
                        iterations_label = get_label("iterations", language)
                        lines.append(f"**{iter_info_label}**{sep}")
                        lines.append(f"- **{iter_count_label}**{sep} {scf_iterations} {iterations_label}")
                        if scf_iter_when_diis_closed is not None:
                            diis_closed_at = get_label("diis_closed_at", language)
                            iterations_after = get_label("iterations_after", language)
                            note_diis = get_label("note_diis_closed", language)
                            if language == "en":
                                lines.append(f"- {diis_closed_at} {scf_iter_when_diis_closed}")
                                lines.append(f"- {note_diis} {scf_iterations} {iterations_label}")
                            else:
                                lines.append(f"- {diis_closed_at} {scf_iter_when_diis_closed}{iterations_after}")
                                lines.append(f"- {note_diis} {scf_iterations} {iterations_label}")
                        lines.append("")
                    
                    conv_criteria_label = get_label("convergence_criteria", language)
                    lines.append(f"**{conv_criteria_label}**{sep}")
                    if thresh_ene is not None:
                        threne_label = "THRENE"
                        if language == "en":
                            lines.append(f"- **{threne_label}** (Energy convergence threshold) = {thresh_ene:.2e} Hartree")
                        else:
                            lines.append(f"- **{threne_label}** (能量收敛阈值) = {thresh_ene:.2e} Hartree")
                        lines.append(f"  - {get_label('threne_desc', language)}")
                    if thresh_den is not None:
                        thrden_label = "THRDEN"
                        if language == "en":
                            lines.append(f"- **{thrden_label}** (Density matrix convergence threshold) = {thresh_den:.2e}")
                        else:
                            lines.append(f"- **{thrden_label}** (密度矩阵收敛阈值) = {thresh_den:.2e}")
                        lines.append(f"  - {get_label('thrden_desc', language)}")
                    lines.append("")
                    
                    if final_deltae is not None or final_deltad is not None:
                        actual_conv_label = get_label("actual_convergence", language)
                        lines.append(f"**{actual_conv_label}**{sep}")
                        if final_deltae is not None:
                            deltae_label = get_label("final_deltae", language)
                            if language == "en":
                                lines.append(f"- **{deltae_label}** = {final_deltae:.2e} Hartree")
                            else:
                                lines.append(f"- **{deltae_label}** = {final_deltae:.2e} Hartree")
                            if thresh_ene is not None:
                                meets_label = get_label("meets_criteria", language)
                                not_meets_label = get_label("not_meets_criteria", language)
                                if abs(final_deltae) < thresh_ene:
                                    if language == "en":
                                        lines.append(f"  - ✓ {meets_label} (|DeltaE| = {abs(final_deltae):.2e} < {thresh_ene:.2e})")
                                    else:
                                        lines.append(f"  - ✓ {meets_label} (|DeltaE| = {abs(final_deltae):.2e} < {thresh_ene:.2e})")
                                else:
                                    if language == "en":
                                        lines.append(f"  - ⚠️ {not_meets_label} (|DeltaE| = {abs(final_deltae):.2e} >= {thresh_ene:.2e})")
                                    else:
                                        lines.append(f"  - ⚠️ {not_meets_label} (|DeltaE| = {abs(final_deltae):.2e} >= {thresh_ene:.2e})")
                            else:
                                if abs(final_deltae) < 1e-7:
                                    lines.append(f"  - ✓ {get_label('energy_change_small', language)}")
                                else:
                                    lines.append(f"  - ⚠️ {get_label('energy_change_large', language)}")
                        
                        if final_deltad is not None:
                            deltad_label = get_label("final_deltad", language)
                            if language == "en":
                                lines.append(f"- **{deltad_label}** = {final_deltad:.2e}")
                            else:
                                lines.append(f"- **{deltad_label}** = {final_deltad:.2e}")
                            if thresh_den is not None:
                                meets_label = get_label("meets_criteria", language)
                                not_meets_label = get_label("not_meets_criteria", language)
                                if abs(final_deltad) < thresh_den:
                                    if language == "en":
                                        lines.append(f"  - ✓ {meets_label} (|DeltaD| = {abs(final_deltad):.2e} < {thresh_den:.2e})")
                                    else:
                                        lines.append(f"  - ✓ {meets_label} (|DeltaD| = {abs(final_deltad):.2e} < {thresh_den:.2e})")
                                else:
                                    if language == "en":
                                        lines.append(f"  - ⚠️ {not_meets_label} (|DeltaD| = {abs(final_deltad):.2e} >= {thresh_den:.2e})")
                                    else:
                                        lines.append(f"  - ⚠️ {not_meets_label} (|DeltaD| = {abs(final_deltad):.2e} >= {thresh_den:.2e})")
                            else:
                                if abs(final_deltad) < 5e-5:
                                    lines.append(f"  - ✓ {get_label('density_change_small', language)}")
                                else:
                                    lines.append(f"  - ⚠️ {get_label('density_change_large', language)}")
                        lines.append("")
                
                # 偶极矩
                dipole = properties.get('dipole')
                if dipole:
                    dipole_title = get_label("dipole_moment", language)
                    lines.append(f"#### {dipole_title}")
                    lines.append("")
                    x_label = get_label("x_component", language)
                    y_label = get_label("y_component", language)
                    z_label = get_label("z_component", language)
                    total_dipole_label = get_label("total_dipole", language)
                    lines.append(f"- **{x_label}**{sep} {dipole.get('x', 0):.6f} {dipole.get('units', 'Debye')}")
                    lines.append(f"- **{y_label}**{sep} {dipole.get('y', 0):.6f} {dipole.get('units', 'Debye')}")
                    lines.append(f"- **{z_label}**{sep} {dipole.get('z', 0):.6f} {dipole.get('units', 'Debye')}")
                    lines.append(f"- **{total_dipole_label}**{sep} {dipole.get('total', 0):.6f} {dipole.get('units', 'Debye')}")
                    lines.append("")
                
                # Mulliken 布居分析
                mulliken_charges = properties.get('mulliken_charges')
                mulliken_spin = properties.get('mulliken_spin_densities')
                if mulliken_charges:
                    mulliken_title = get_label("mulliken_analysis", language)
                    lines.append(f"#### {mulliken_title}")
                    lines.append("")
                    atom_label_text = get_label("atom_label", language)
                    charge_label = get_label("charge", language)
                    spin_label = get_label("spin_density", language) if mulliken_spin else ""
                    header = f"| {atom_label_text} | {charge_label} |"
                    if mulliken_spin:
                        header += f" {spin_label} |"
                    lines.append(header)
                    sep_line = "|------|------|"
                    if mulliken_spin:
                        sep_line += "----------|"
                    lines.append(sep_line)
                    for atom_label, charge in sorted(mulliken_charges.items()):
                        spin_val = mulliken_spin.get(atom_label) if mulliken_spin else None
                        if spin_val is not None:
                            lines.append(f"| {atom_label} | {charge:8.4f} | {spin_val:8.4f} |")
                        else:
                            lines.append(f"| {atom_label} | {charge:8.4f} |")
                    lines.append("")
                    note_label = get_label("note", language)
                    mulliken_desc = get_label("mulliken_desc", language)
                    lines.append(f"**{note_label}**{sep} {mulliken_desc}")
                    lines.append("")
                
                # Lowdin 布居分析
                lowdin_charges = properties.get('lowdin_charges')
                lowdin_spin = properties.get('lowdin_spin_densities')
                if lowdin_charges:
                    lowdin_title = get_label("lowdin_analysis", language)
                    lines.append(f"#### {lowdin_title}")
                    lines.append("")
                    atom_label_text = get_label("atom_label", language)
                    charge_label = get_label("charge", language)
                    spin_label = get_label("spin_density", language) if lowdin_spin else ""
                    header = f"| {atom_label_text} | {charge_label} |"
                    if lowdin_spin:
                        header += f" {spin_label} |"
                    lines.append(header)
                    sep_line = "|------|------|"
                    if lowdin_spin:
                        sep_line += "----------|"
                    lines.append(sep_line)
                    for atom_label, charge in sorted(lowdin_charges.items()):
                        spin_val = lowdin_spin.get(atom_label) if lowdin_spin else None
                        if spin_val is not None:
                            lines.append(f"| {atom_label} | {charge:8.4f} | {spin_val:8.4f} |")
                        else:
                            lines.append(f"| {atom_label} | {charge:8.4f} |")
                    lines.append("")
                    note_label = get_label("note", language)
                    lowdin_desc = get_label("lowdin_desc", language)
                    lines.append(f"**{note_label}**{sep} {lowdin_desc}")
                    lines.append("")
            
            # 显示溶剂效应信息
            solvent = properties.get('solvent')
            if solvent:
                lines.append("")
                solvent_title = get_label("solvent_effect", language)
                lines.append(f"#### {solvent_title}")
                lines.append("")
                
                if solvent.get('implicit_solvent'):
                    implicit_note = get_label("implicit_solvent_note", language)
                    lines.append(f"- {implicit_note}")
                    lines.append("")
                
                noneq_method = properties.get('solvent_noneq_method')
                if noneq_method:
                    method_label = get_label("noneq_method", language)
                    if noneq_method == "clr_linear_response":
                        method_desc = get_label("noneq_method_clr", language)
                    elif noneq_method == "ptSS_state_specific":
                        method_desc = get_label("noneq_method_ptss", language)
                    else:
                        method_desc = noneq_method
                    lines.append(f"- **{method_label}**{sep} {method_desc}")
                
                if solvent.get('method'):
                    method_label = get_label("solvent_method", language)
                    lines.append(f"- **{method_label}**{sep} {solvent['method']}")
                
                if solvent.get('solvent'):
                    solvent_label = get_label("solvent_name", language)
                    lines.append(f"- **{solvent_label}**{sep} {solvent['solvent']}")
                
                if solvent.get('dielectric_constant') is not None:
                    dielectric_label = get_label("dielectric_constant", language)
                    lines.append(f"- **{dielectric_label}**{sep} {solvent['dielectric_constant']:.6f}")
                
                if solvent.get('optical_dielectric_constant') is not None:
                    optical_label = get_label("optical_dielectric_constant", language)
                    lines.append(f"- **{optical_label}**{sep} {solvent['optical_dielectric_constant']:.6f}")
                
                if solvent.get('tessellation_method'):
                    tessellation_label = get_label("tessellation_method", language)
                    lines.append(f"- **{tessellation_label}**{sep} {solvent['tessellation_method']}")
                
                if solvent.get('radius_type'):
                    radius_label = get_label("radius_type", language)
                    lines.append(f"- **{radius_label}**{sep} {solvent['radius_type']}")
                
                if solvent.get('mesh_accuracy'):
                    mesh_label = get_label("mesh_accuracy", language)
                    lines.append(f"- **{mesh_label}**{sep} {solvent['mesh_accuracy']}")
                
                if solvent.get('num_tesseraes') is not None:
                    tesseraes_label = get_label("num_tesseraes", language)
                    lines.append(f"- **{tesseraes_label}**{sep} {solvent['num_tesseraes']}")
                
                lines.append("")
                solvent_calc_note = get_label("solvent_calculation_note", language)
                lines.append(f"**{note_label}**{sep} {solvent_calc_note}")
                lines.append("")
            
            # 非平衡溶剂化校正信息
            noneq_corr = properties.get('solvent_noneq_corrections')
            if noneq_corr:
                lines.append("")
                solvent_effect = get_label("solvent_effect", language)
                lines.append(f"#### {solvent_effect} - cLR")
                lines.append("")
                # 表头
                state_label = get_label("state", language)
                corr_energy_label = get_label("corrected_vertical_energy", language)
                noneq_label = get_label("noneq_solvation_free_energy", language)
                eq_label = get_label("eq_solvation_free_energy", language)
                clr_label = get_label("clr_correction", language)
                lines.append(f"| {state_label} | {corr_energy_label} (eV) | {noneq_label} (eV) | {eq_label} (eV) | {clr_label} (eV) |")
                lines.append("|------|----------------------|---------------------------|--------------------------|--------------------|")
                for corr in noneq_corr:
                    st = corr.get('state_index')
                    cv = corr.get('corrected_vertical_energy_ev')
                    ne = corr.get('noneq_solvation_free_energy_ev')
                    eq = corr.get('eq_solvation_free_energy_ev')
                    clr = corr.get('excitation_energy_correction_ev')
                    lines.append(f"| {st} | {cv:8.4f} | {ne:8.4f} | {eq:8.4f} | {clr:8.4f} |")
                lines.append("")
            
            frequencies = parsed_data.get('frequencies', [])
            if frequencies:
                if language == "en":
                    lines.append(f"- **Number of Vibrational Frequencies**: {len(frequencies)}")
                else:
                    lines.append(f"- **振动频率数量**：{len(frequencies)}")
            
            # TDDFT 信息
            tddft = parsed_data.get('tddft', [])
            if tddft:
                lines.append("")
                tddft_title = get_label("tddft_results", language)
                lines.append(f"### {tddft_title}")
                lines.append("")
                for idx, calc in enumerate(tddft, 1):
                    tddft_block_label = get_label("tddft_block", language)
                    lines.append(f"#### {tddft_block_label} {idx}")
                    lines.append("")
                    
                    # 显示近似方法
                    approx_method = calc.get('approximation_method')
                    itda = calc.get('itda')
                    if approx_method:
                        method_label = get_label("calculation_method", language)
                        lines.append(f"- **{method_label}**{sep} {approx_method}")
                    if itda is not None:
                        itda_label = get_label("itda_parameter", language)
                        lines.append(f"- **{itda_label}**{sep} {itda}")
                        if itda == 1:
                            tda_note = get_label("tda_note", language)
                            lines.append(f"  - {tda_note}")
                        elif itda == 0:
                            tddft_note = get_label("tddft_note", language)
                            lines.append(f"  - {tddft_note}")
                    
                    # 显示其他参数
                    isf = calc.get('isf')
                    is_spin_flip = (isf is not None and isf != 0)
                    
                    if isf is not None:
                        spin_dir = calc.get('spin_flip_direction')
                        if spin_dir:
                            isf_label = get_label("spin_flip_direction", language)
                            lines.append(f"- **{isf_label}**{sep} {isf} ({spin_dir})")
                        else:
                            isf_param_label = get_label("spin_flip_parameter", language)
                            lines.append(f"- **{isf_param_label}**{sep} {isf}")
                        
                        # 添加 spin-flip 计算的说明
                        if is_spin_flip:
                            spin_flip_calc = get_label("spin_flip_calculation", language)
                            this_is_spin_flip = get_label("this_is_spin_flip", language)
                            isf_note = get_label("isf_not_zero_note", language)
                            spin_flip_feature = get_label("spin_flip_feature", language)
                            important = get_label("oscillator_zero_important", language)
                            osc_zero_note = get_label("oscillator_zero_note", language)
                            osc_zero_reason = get_label("oscillator_zero_reason", language)
                            osc_zero_expected = get_label("oscillator_zero_expected", language)
                            lines.append(f"  - ⚠️ **{spin_flip_calc}**{sep} {this_is_spin_flip}")
                            lines.append(f"  - {isf_note}")
                            lines.append(f"  - {spin_flip_feature}")
                            lines.append(f"  - **{important}**{sep} {osc_zero_note}")
                            lines.append(f"    - {osc_zero_reason}")
                            lines.append(f"    - {osc_zero_expected}")
                    
                    ialda = calc.get('ialda')
                    if ialda is not None:
                        ialda_label = get_label("ialda_parameter", language)
                        lines.append(f"- **{ialda_label}**{sep} {ialda}")
                    
                    method = calc.get('method')
                    if method:
                        method_label = get_label("method", language)
                        lines.append(f"- **{method_label}**{sep} {method}")
                    
                    # 显示 JK 算符内存信息
                    jk_estimated = calc.get('jk_estimated_memory_mb')
                    jk_max = calc.get('jk_max_memory_mb')
                    rpa_roots = calc.get('rpa_roots_per_pass')
                    tda_roots = calc.get('tda_roots_per_pass')
                    roots_per_pass = calc.get('roots_per_pass')
                    n_exit = calc.get('n_exit')
                    
                    if jk_estimated is not None or jk_max is not None or roots_per_pass is not None:
                        lines.append("")
                        jk_memory_title = get_label("jk_memory_info", language)
                        lines.append(f"- **{jk_memory_title}**{sep}")
                        if jk_estimated is not None:
                            jk_est_label = get_label("jk_estimated_memory", language)
                            memory_mb = get_label("memory_mb", language)
                            lines.append(f"  - **{jk_est_label}**{sep} {jk_estimated:.3f} {memory_mb}")
                            jk_mem_note = get_label("jk_memory_note", language)
                            lines.append(f"    - {jk_mem_note}")
                        if jk_max is not None:
                            jk_max_label = get_label("jk_max_memory", language)
                            memory_mb = get_label("memory_mb", language)
                            lines.append(f"  - **{jk_max_label}**{sep} {jk_max:.3f} {memory_mb}")
                            jk_max_note = get_label("jk_max_memory_note", language)
                            lines.append(f"    - {jk_max_note}")
                        if rpa_roots is not None:
                            rpa_label = get_label("rpa_roots_per_pass", language)
                            lines.append(f"  - **{rpa_label}**{sep} {rpa_roots}")
                            rpa_note = get_label("rpa_roots_note", language)
                            lines.append(f"    - {rpa_note}")
                        if tda_roots is not None:
                            tda_label = get_label("tda_roots_per_pass", language)
                            lines.append(f"  - **{tda_label}**{sep} {tda_roots}")
                            tda_note = get_label("tda_roots_note", language)
                            lines.append(f"    - {tda_note}")
                        if roots_per_pass is not None:
                            roots_label = get_label("roots_per_pass", language)
                            if language == "en":
                                lines.append(f"  - **{roots_label}** (current calculation){sep} {roots_per_pass}")
                            else:
                                lines.append(f"  - **{roots_label}** (当前计算){sep} {roots_per_pass}")
                        if n_exit is not None:
                            nexit_label = get_label("n_exit_requested", language)
                            lines.append(f"  - **{nexit_label}**{sep} {n_exit}")
                        
                        # 效率提示
                        if n_exit is not None and roots_per_pass is not None:
                            lines.append("")
                            if n_exit > roots_per_pass:
                                efficiency_warning = get_label("efficiency_warning", language)
                                roots_greater = get_label("roots_greater_than_pass", language)
                                lines.append(f"  - ⚠️ **{efficiency_warning}**{sep} {roots_greater}")
                                lines.append(f"    - {n_exit} > {roots_per_pass}")
                                efficiency_rec = get_label("efficiency_recommendation", language)
                                lines.append(f"    - **{efficiency_rec}**")
                                memjkop_format = get_label("memjkop_format", language)
                                memjkop_note = get_label("memjkop_note", language)
                                lines.append(f"    - {memjkop_format}")
                                lines.append(f"    - {memjkop_note}")
                            else:
                                roots_within = get_label("roots_within_limit", language)
                                lines.append(f"  - ✓ {roots_within}")
                    
                    # 显示激发态数量
                    states = calc.get('states', [])
                    if states:
                        state_count_label = get_label("excited_state_count", language)
                        lines.append(f"- **{state_count_label}**{sep} {len(states)}")
                        lines.append("")
                        
                        # 检查是否所有振子强度都为0
                        all_osc_zero = all(state.get('oscillator_strength', 0) == 0 for state in states[:5])
                        
                        first_5_states = get_label("first_5_states", language)
                        state_label = get_label("state", language)
                        energy_label = get_label("energy", language)
                        wavelength_label = get_label("wavelength", language)
                        osc_label = get_label("oscillator_strength", language)
                        lines.append(f"  {first_5_states}{sep}")
                        for state in states[:5]:
                            idx_state = state.get('index', '?')
                            energy = state.get('energy_ev', 0)
                            wavelength = state.get('wavelength_nm', 0)
                            osc = state.get('oscillator_strength', 0)
                            osc_str = f"{osc:.6f}"
                            if is_spin_flip and osc == 0:
                                spin_flip_normal = get_label("spin_flip_normal", language)
                                osc_str += f" ({spin_flip_normal})"
                            if language == "en":
                                lines.append(f"    - {state_label} {idx_state}{sep} {energy_label} = {energy:.4f} eV, "
                                           f"{wavelength_label} = {wavelength:.2f} nm, "
                                           f"{osc_label} = {osc_str}")
                            else:
                                lines.append(f"    - {state_label} {idx_state}{sep} {energy_label} = {energy:.4f} eV, "
                                           f"{wavelength_label} = {wavelength:.2f} nm, "
                                           f"{osc_label} = {osc_str}")
                        
                        # 如果所有振子强度为0且是spin-flip计算，添加说明
                        if is_spin_flip and all_osc_zero:
                            lines.append("")
                            all_osc_zero_note = get_label("all_oscillator_zero", language)
                            spin_flip_forbidden = get_label("spin_flip_forbidden", language)
                            mag_quad = get_label("magnetic_quadrupole", language)
                            note_label_text = get_label("note", language)
                            lines.append(f"  **{note_label_text}**{sep} {all_osc_zero_note}")
                            lines.append(f"  - {spin_flip_forbidden}")
                            lines.append(f"  - {mag_quad}")
                    lines.append("")
            
            lines.append("")
        
        # 建议
        recommendations = analysis_result.get('recommendations', [])
        if recommendations:
            rec_title = get_label("recommendations", language)
            lines.append(f"## {rec_title}")
            lines.append("")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        # 警告
        warnings = analysis_result.get('warnings', [])
        if warnings:
            warnings_title = get_label("warnings", language)
            lines.append(f"## {warnings_title}")
            lines.append("")
            for i, warning in enumerate(warnings, 1):
                lines.append(f"{i}. {warning}")
            lines.append("")
        
        # 专家见解
        expert_insights = analysis_result.get('expert_insights', '')
        if expert_insights:
            insights_title = get_label("expert_insights", language)
            lines.append(f"## {insights_title}")
            lines.append("")
            lines.append(expert_insights)
            lines.append("")
        
        # 如果没有结构化内容，显示原始分析
        raw_analysis = analysis_result.get('raw_analysis', '')
        if raw_analysis and not (summary or energy_analysis or geometry_analysis):
            ai_analysis_title = get_label("ai_analysis", language)
            lines.append(f"## {ai_analysis_title}")
            lines.append("")
            lines.append(raw_analysis)
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_html(
        self,
        analysis_result: Dict[str, Any],
        parsed_data: Optional[Dict[str, Any]] = None,
        language: Language = "zh"
    ) -> str:
        """生成 HTML 格式报告"""
        # 先生成 Markdown，然后转换为 HTML（简化版本）
        markdown = self._generate_markdown(analysis_result, parsed_data, language)
        
        # 简单的 Markdown 到 HTML 转换
        html_lines = []
        html_lines.append("<!DOCTYPE html>")
        html_lines.append("<html>")
        html_lines.append("<head>")
        html_lines.append('<meta charset="utf-8">')
        html_lines.append("<title>BDF 计算结果分析报告</title>")
        html_lines.append('<style>')
        html_lines.append('body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }')
        html_lines.append('h1 { color: #333; }')
        html_lines.append('h2 { color: #666; margin-top: 30px; }')
        html_lines.append('pre { background: #f5f5f5; padding: 10px; border-radius: 5px; }')
        html_lines.append('</style>')
        html_lines.append("</head>")
        html_lines.append("<body>")
        
        # 简单的 Markdown 转换
        import re
        html_content = markdown
        
        # 标题转换
        html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        
        # 粗体
        html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
        
        # 列表
        html_content = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', html_content, flags=re.MULTILINE)
        
        # 段落
        paragraphs = html_content.split('\n\n')
        html_paragraphs = []
        for para in paragraphs:
            if para.strip() and not para.startswith('<'):
                html_paragraphs.append(f'<p>{para}</p>')
            else:
                html_paragraphs.append(para)
        
        html_lines.append('\n'.join(html_paragraphs))
        html_lines.append("</body>")
        html_lines.append("</html>")
        
        return "\n".join(html_lines)
    
    def _generate_text(
        self,
        analysis_result: Dict[str, Any],
        parsed_data: Optional[Dict[str, Any]] = None,
        language: Language = "zh"
    ) -> str:
        """生成纯文本格式报告"""
        # 先生成 Markdown，然后去除 Markdown 标记
        markdown = self._generate_markdown(analysis_result, parsed_data, language)
        
        # 简单的 Markdown 到文本转换
        import re
        
        # 移除标题标记
        text = re.sub(r'^#+\s+', '', markdown, flags=re.MULTILINE)
        
        # 移除粗体标记
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        
        # 移除代码块标记
        text = re.sub(r'```[\w]*\n', '', text)
        
        return text

