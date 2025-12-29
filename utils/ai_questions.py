"""AI Questions Module - Handles generation of AI questions based on research data"""

import logging

logger = logging.getLogger(__name__)

def generate_ai_questions(research_results, idea):
    """Generate AI questions based on research data and idea context - NO FALLBACKS"""
    try:
        # Extract key insights from research
        existing_solutions = research_results.get('existing_solutions', [])
        competitors = research_results.get('competitors', [])
        trends = research_results.get('trends', [])
        opportunities = research_results.get('opportunities', [])
        challenges = research_results.get('challenges', [])
        
        idea_title = idea.get('title', '')
        idea_text = idea.get('rephrased_idea', '')
        
        # Generate questions based on ACTUAL research insights only
        questions = []
        
        # Only add questions if we have real research data
        if existing_solutions:
            solution_names = ', '.join([sol.get('title', '') for sol in existing_solutions[:3]])
            questions.append(f"Given that solutions like {solution_names} exist, how does '{idea_title}' address gaps they don't cover?")
            questions.append(f"What customer pain points do {solution_names} fail to address that '{idea_title}' specifically solves?")
        
        if competitors:
            competitor_names = ', '.join([comp.get('name', '') for comp in competitors[:3]])
            questions.append(f"How would '{idea_title}' compete against {competitor_names} in terms of features, pricing, and user experience?")
        
        if trends:
            trend_list = ', '.join([t.get('trend', '') for t in trends[:2]])
            questions.append(f"How does '{idea_title}' leverage the trends: {trend_list}?")
        
        if opportunities:
            opp_list = ', '.join(opportunities[:2])
            questions.append(f"How can '{idea_title}' capitalize on these market opportunities: {opp_list}?")
        
        if challenges:
            challenge_list = ', '.join(challenges[:2])
            questions.append(f"How will '{idea_title}' overcome these market challenges: {challenge_list}?")
        
        # Only return questions that were actually generated from research
        return questions if questions else None
        
    except Exception as e:
        logger.error(f"Error generating AI questions: {str(e)}")
        return None

def generate_ai_development_questions(research_results, idea):
    """Generate ONLY research-based development questions - NO GENERIC FALLBACKS"""
    try:
        import streamlit as st
        
        # Get max questions from session state (set by slider in research_analysis.py)
        # Fall back to 5 if not set
        TESTING_MAX_QUESTIONS = st.session_state.get('testing_max_questions', 5)
        
        # Extract key insights from research
        existing_solutions = research_results.get('existing_solutions', [])
        competitors = research_results.get('competitors', [])
        trends = research_results.get('trends', [])
        opportunities = research_results.get('opportunities', [])
        challenges = research_results.get('challenges', [])
        
        idea_title = idea.get('title', '')
        
        # Build ONLY from actual research data
        dev_questions = []
        
        # Q1: Problem - Use actual research context
        if existing_solutions or opportunities:
            context = ""
            if existing_solutions:
                context = f"Research found {len(existing_solutions)} existing solutions"
            if opportunities:
                context += f" with opportunity: {opportunities[0]}" if context else f"Research identified opportunity: {opportunities[0]}"
            
            problem_q = f"What specific customer problem does '{idea_title}' solve? ({context})"
            dev_questions.append({
                "section": "Executive Summary",
                "question": problem_q,
                "key": "q_problem"
            })
        
        # Q2: Differentiation - ONLY if we have competition data
        if (existing_solutions or competitors) and len(dev_questions) < TESTING_MAX_QUESTIONS:
            if existing_solutions and len(existing_solutions) > 0:
                sol_names = ', '.join([s.get('title', '') for s in existing_solutions[:2]])
                diff_q = f"How is '{idea_title}' different from {sol_names}? What specific gaps do they miss?"
            elif competitors and len(competitors) > 0:
                comp_names = ', '.join([c.get('name', '') for c in competitors[:2]])
                diff_q = f"How does '{idea_title}' differentiate from competitors like {comp_names}?"
            else:
                diff_q = f"What makes '{idea_title}' unique in this market?"
            
            dev_questions.append({
                "section": "Executive Summary", 
                "question": diff_q,
                "key": "q_differentiate"
            })
        
        # Q3: Value - ONLY if we have opportunity data
        if opportunities and len(dev_questions) < TESTING_MAX_QUESTIONS:
            value_q = f"What measurable benefits will '{idea_title}' deliver? Focus on: {', '.join(opportunities[:2])}"
            dev_questions.append({
                "section": "Business Value",
                "question": value_q,
                "key": "q_value"
            })
        
        # Q4: ROI Analysis - NEW ROI QUESTION
        if (existing_solutions or competitors or opportunities) and len(dev_questions) < TESTING_MAX_QUESTIONS:
            roi_context = []
            if existing_solutions:
                roi_context.append(f"{len(existing_solutions)} existing solutions")
            if competitors:
                roi_context.append(f"{len(competitors)} competitors")
            if opportunities:
                roi_context.append(f"{len(opportunities)} market opportunities")
            
            roi_q = f"Based on market research showing {', '.join(roi_context)}, what is the expected ROI and financial viability of '{idea_title}'?"
            dev_questions.append({
                "section": "ROI Analysis",
                "question": roi_q,
                "key": "q_roi"
            })
        
        # Q5: Implementation - ONLY if we have trend data
        if trends and len(dev_questions) < TESTING_MAX_QUESTIONS:
            trend_context = ', '.join([t.get('trend', '') for t in trends[:2]])
            impl_q = f"What are the key implementation steps for '{idea_title}'? Consider trends: {trend_context}"
            dev_questions.append({
                "section": "Implementation Plan",
                "question": impl_q,
                "key": "q_steps"
            })
        
        # Q6: Risks - ONLY if we have challenge data
        if challenges and len(dev_questions) < TESTING_MAX_QUESTIONS:
            challenge_context = ', '.join(challenges[:2])
            risk_q = f"How will '{idea_title}' address these market challenges: {challenge_context}?"
            dev_questions.append({
                "section": "Risk Analysis",
                "question": risk_q,
                "key": "q_risks"
            })
        
        logger.info(f"Generated {len(dev_questions)} research-specific questions for: {idea_title} (TESTING_MAX_QUESTIONS={TESTING_MAX_QUESTIONS})")
        
        # Return ONLY questions generated from actual research - NO FALLBACKS
        return dev_questions if dev_questions else None
        
    except Exception as e:
        logger.error(f"Error generating AI development questions: {str(e)}")
        return None
