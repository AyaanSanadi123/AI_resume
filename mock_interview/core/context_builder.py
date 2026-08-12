
def build_interview_context(parsed_resume: dict, github_context: str = "", target_role: str = "AI Engineer") -> str:
    
    name = parsed_resume.get("name", "Candidate")
    skills = ", ".join(parsed_resume.get("skills", []))
    experience = parsed_resume.get("experience", [])
    projects = parsed_resume.get("projects", [])

    # Format the resume into clean markdown blocks
    markdown_context = f"""
    === CANDIDATE BACKGROUND ===
    Name: {name}
    Target Role: {target_role}
    Core Technical Skills: {skills}

    === WORK EXPERIENCE & KEY PROJECTS ===
    Experience Entries:
    {experience}

    Project Highlights:
    {projects}

    === GITHUB CODE & REPOSITORY ANALYSIS ===
    {github_context if github_context else "No external GitHub repositories provided for this session."}
    """
    
    return markdown_context.strip()