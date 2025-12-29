"""UI Components for Score Explanation - 'Why this score?' expandable section"""

import streamlit as st
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


def render_score_explanation_section(explanation: Dict[str, Any], idea_title: str = "Idea"):
    """
    Render the 'Why this score?' expandable section with full transparency
    
    Args:
        explanation: Output from EnhancedAIScoreService.get_score_explanation()
        idea_title: Title of the idea being explained
    """
    if not explanation.get("success"):
        st.warning("Score explanation not available")
        return
    
    with st.expander("🔍 **Why this score?** - Click to see detailed analysis", expanded=False):
        # Overall score and confidence header
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            total_score = explanation.get("total_score", 0)
            score_color = _get_score_color(total_score)
            st.markdown(f"""
            <div style='text-align: center; padding: 10px; background-color: {score_color}20; border-radius: 10px;'>
                <h2 style='margin: 0; color: {score_color};'>{total_score}/100</h2>
                <p style='margin: 0; color: #666;'>Total Score</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            confidence = explanation.get("overall_confidence", 0.5)
            confidence_pct = round(confidence * 100)
            confidence_label = explanation.get("confidence_label", "Moderate")
            st.markdown(f"""
            <div style='text-align: center; padding: 10px; background-color: #f0f0f0; border-radius: 10px;'>
                <h2 style='margin: 0; color: #333;'>{confidence_pct}%</h2>
                <p style='margin: 0; color: #666;'>{confidence_label}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            bias_count = len(explanation.get("bias_alerts", []))
            high_severity = sum(1 for b in explanation.get("bias_alerts", []) if b.get("severity") == "high")
            warning_color = "#dc3545" if high_severity > 0 else "#ffc107" if bias_count > 0 else "#28a745"
            st.markdown(f"""
            <div style='text-align: center; padding: 10px; background-color: {warning_color}20; border-radius: 10px;'>
                <h2 style='margin: 0; color: {warning_color};'>{bias_count}</h2>
                <p style='margin: 0; color: #666;'>Data Warnings</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Bias Warnings Section (show prominently if any high severity)
        bias_alerts = explanation.get("bias_alerts", [])
        if bias_alerts:
            st.markdown("### ⚠️ Data Quality & Bias Warnings")
            for alert in bias_alerts:
                severity = alert.get("severity", "low")
                icon = alert.get("icon", "⚪")
                
                if severity == "high":
                    container_style = "background-color: #ffebee; border-left: 4px solid #dc3545;"
                elif severity == "medium":
                    container_style = "background-color: #fff8e1; border-left: 4px solid #ffc107;"
                else:
                    container_style = "background-color: #e8f5e9; border-left: 4px solid #28a745;"
                
                st.markdown(f"""
                <div style='padding: 10px 15px; margin: 5px 0; border-radius: 5px; {container_style}'>
                    <strong>{icon} {alert.get("type", "Warning").replace("_", " ").title()}</strong>
                    <p style='margin: 5px 0;'>{alert.get("description", "")}</p>
                    <small style='color: #666;'>💡 <em>{alert.get("mitigation", "")}</em></small>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
        
        # Per-Criterion Breakdown
        st.markdown("### 📊 Score Breakdown by Criterion")
        
        criteria = explanation.get("criteria_breakdown", [])
        for criterion in criteria:
            _render_criterion_card(criterion)
        
        st.markdown("---")
        
        # Strengths and Improvements
        col_s, col_i = st.columns(2)
        
        with col_s:
            st.markdown("### ✅ Strengths")
            for strength in explanation.get("strengths", []):
                st.markdown(f"- {strength}")
        
        with col_i:
            st.markdown("### 🔧 Areas for Improvement")
            for improvement in explanation.get("improvements", []):
                st.markdown(f"- {improvement}")
        
        # Data Quality Notes
        if explanation.get("data_quality"):
            st.markdown("---")
            st.markdown("### 📋 Data Quality Assessment")
            st.info(explanation.get("data_quality"))


def _render_criterion_card(criterion: Dict[str, Any]):
    """Render a single criterion card with score, reasoning, and evidence"""
    name = criterion.get("name", "Unknown")
    score = criterion.get("score", 0)
    max_score = criterion.get("max_score", 25)
    percentage = criterion.get("percentage", 0)
    reasoning = criterion.get("reasoning", "")
    evidence = criterion.get("evidence", [])
    confidence = criterion.get("confidence", 0.5)
    confidence_label = criterion.get("confidence_label", "Moderate")
    
    # Color based on percentage
    if percentage >= 75:
        bar_color = "#28a745"
    elif percentage >= 50:
        bar_color = "#ffc107"
    else:
        bar_color = "#dc3545"
    
    # Criterion icon mapping
    icons = {
        "Innovation": "💡",
        "Feasibility": "🔧",
        "Business Impact": "📈",
        "Clarity": "📝"
    }
    icon = icons.get(name, "📌")
    
    with st.container():
        st.markdown(f"""
        <div style='background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 10px; border-left: 4px solid {bar_color};'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <h4 style='margin: 0;'>{icon} {name}</h4>
                <span style='background-color: {bar_color}; color: white; padding: 5px 15px; border-radius: 15px; font-weight: bold;'>
                    {score}/{max_score}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        st.progress(percentage / 100)
        
        # Reasoning
        st.markdown(f"**Reasoning:** {reasoning}")
        
        # Evidence bullets
        if evidence:
            st.markdown("**Evidence from your idea:**")
            for e in evidence[:3]:  # Limit to 3 pieces of evidence
                st.markdown(f"- *\"{e}\"*")
        
        # Confidence indicator
        conf_color = "#28a745" if confidence >= 0.7 else "#ffc107" if confidence >= 0.4 else "#dc3545"
        st.markdown(f"""
        <small style='color: {conf_color};'>
            🎯 {confidence_label} ({round(confidence * 100)}% confident in this assessment)
        </small>
        """, unsafe_allow_html=True)
        
        st.markdown("")  # Spacing


def _get_score_color(score: int) -> str:
    """Get color based on score"""
    if score >= 75:
        return "#28a745"  # Green
    elif score >= 50:
        return "#ffc107"  # Yellow
    else:
        return "#dc3545"  # Red


def render_compact_score_badge(score: int, confidence: float = None, show_confidence: bool = True):
    """
    Render a compact score badge for list views
    
    Args:
        score: The score value (0-100)
        confidence: Optional confidence value (0.0-1.0)
        show_confidence: Whether to show confidence indicator
    """
    color = _get_score_color(score)
    
    confidence_html = ""
    if show_confidence and confidence is not None:
        conf_icon = "🟢" if confidence >= 0.7 else "🟡" if confidence >= 0.4 else "🔴"
        confidence_html = f"<small>{conf_icon}</small>"
    
    st.markdown(f"""
    <div style='display: inline-flex; align-items: center; gap: 5px;'>
        <span style='background-color: {color}; color: white; padding: 3px 10px; border-radius: 10px; font-weight: bold;'>
            {score}
        </span>
        {confidence_html}
    </div>
    """, unsafe_allow_html=True)


def render_quick_bias_indicator(bias_warnings: List[Dict[str, Any]]):
    """
    Render a quick indicator for bias warnings in list views
    
    Args:
        bias_warnings: List of bias warning dictionaries
    """
    if not bias_warnings:
        st.markdown("✅ No data concerns")
        return
    
    high_count = sum(1 for w in bias_warnings if w.get("severity") == "high")
    med_count = sum(1 for w in bias_warnings if w.get("severity") == "medium")
    low_count = sum(1 for w in bias_warnings if w.get("severity") == "low")
    
    indicators = []
    if high_count:
        indicators.append(f"🔴 {high_count}")
    if med_count:
        indicators.append(f"🟡 {med_count}")
    if low_count:
        indicators.append(f"🟢 {low_count}")
    
    st.markdown(" ".join(indicators) + " warnings")
