"""
Method Recommender

This module provides method recommendations based on molecule characteristics.
"""

from typing import Dict, Any, List, Optional


class MethodRecommender:
    """Recommends computational methods based on molecule characteristics."""
    
    # Transition metal elements
    TRANSITION_METALS = [
        "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
        "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd",
        "La", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
        "Ac", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn"
    ]
    
    # Lanthanides and Actinides
    LANTHANIDES = [
        "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy",
        "Ho", "Er", "Tm", "Yb", "Lu"
    ]
    
    ACTINIDES = [
        "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf",
        "Es", "Fm", "Md", "No", "Lr"
    ]
    
    def recommend(
        self,
        molecule_info: Dict[str, Any],
        task_type: str = "energy"
    ) -> Dict[str, Any]:
        """
        Recommend computational method based on molecule characteristics.
        
        Args:
            molecule_info: Dictionary containing:
                - elements: List of element symbols
                - num_atoms: Number of atoms
                - charge: Charge
                - has_heavy_elements: Whether heavy elements are present
            task_type: Type of calculation (energy, optimize, frequency, tddft)
        
        Returns:
            Dictionary with recommendations:
                - functional: Recommended functional
                - basis: Recommended basis set
                - reason: Reason for recommendation
                - warnings: List of warnings
        """
        elements = molecule_info.get("elements", [])
        num_atoms = molecule_info.get("num_atoms", 0)
        charge = molecule_info.get("charge", 0)
        
        has_transition_metal = any(
            elem in self.TRANSITION_METALS for elem in elements
        )
        has_lanthanide = any(elem in self.LANTHANIDES for elem in elements)
        has_actinide = any(elem in self.ACTINIDES for elem in elements)
        has_heavy = has_transition_metal or has_lanthanide or has_actinide
        
        recommendations = {
            "functional": "pbe0",
            "basis": "cc-pvdz",
            "reason": "General recommendation for organic molecules",
            "warnings": []
        }
        
        # Recommendations based on element types
        if has_actinide:
            recommendations["functional"] = "pbe"
            recommendations["basis"] = "def2-tzvp"
            recommendations["reason"] = "Actinide elements detected - using relativistic basis"
            recommendations["warnings"].append(
                "Actinides require special treatment. Consider using relativistic methods."
            )
        elif has_lanthanide:
            recommendations["functional"] = "pbe0"
            recommendations["basis"] = "def2-tzvp"
            recommendations["reason"] = "Lanthanide elements detected - using relativistic basis"
        elif has_transition_metal:
            recommendations["functional"] = "pbe0"
            recommendations["basis"] = "def2-tzvp"
            recommendations["reason"] = "Transition metal detected - using relativistic basis"
        
        # Size-based recommendations
        if num_atoms > 100:
            # For large systems, use smaller basis
            if recommendations["basis"] == "cc-pvdz":
                recommendations["basis"] = "6-31g*"
            recommendations["warnings"].append(
                f"Large system ({num_atoms} atoms) - using smaller basis for efficiency"
            )
        elif num_atoms < 10 and not has_heavy:
            # For small systems, can use larger basis
            recommendations["basis"] = "cc-pvtz"
            recommendations["reason"] += " - small system, can use larger basis"
        
        # Task-specific recommendations
        if task_type == "tddft":
            # TDDFT works well with hybrid functionals
            if recommendations["functional"] == "pbe":
                recommendations["functional"] = "pbe0"
                recommendations["reason"] += " - TDDFT benefits from hybrid functional"
        elif task_type == "optimize":
            # Optimization might benefit from faster convergence
            if num_atoms > 50:
                recommendations["warnings"].append(
                    "Large system for optimization - consider using coarse grid or smaller basis"
                )
        
        return recommendations
    
    def get_recommendation_text(self, molecule_info: Dict[str, Any], task_type: str = "energy") -> str:
        """
        Get human-readable recommendation text.
        
        Args:
            molecule_info: Molecule information dictionary.
            task_type: Task type.
        
        Returns:
            Recommendation text string.
        """
        rec = self.recommend(molecule_info, task_type)
        
        text = f"推荐方法：{rec['functional'].upper()} / {rec['basis']}\n"
        text += f"原因：{rec['reason']}\n"
        
        if rec['warnings']:
            text += "\n注意事项：\n"
            for warning in rec['warnings']:
                text += f"- {warning}\n"
        
        return text

