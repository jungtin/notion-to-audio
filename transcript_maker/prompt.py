def create_educational_transcript_prompt(topic, content, part_number=0, total_parts=1, part_info=""):
    """
    Generates a prompt for creating an educational transcript from technical content.

    Args:
        topic (str): The overall topic of the educational material.
        content (str): The raw technical content to be converted.
        part_number (int, optional): The current part number (for multi-part series). Defaults to 0.
        total_parts (int, optional): The total number of parts in the series. Defaults to 1.
        part_info (str, optional):  Information about the specific part (e.g., "This part focuses on..."). Defaults to "".

    Returns:
        str: The formatted prompt string.
    """

    prompt = f"""
        You're creating an educational transcript for a video or podcast about: {topic}
        Please convert the following technical content into a natural, conversational transcript format. {part_info}

        REQUIREMENTS:
        1.  Include all key information from the original content.
        2.  Use a friendly, educational tone that's easy to understand.  Speak like you're explaining it to a friend, not lecturing. Use contractions, informal phrasing where appropriate, and a friendly tone.
        3.  Add natural transitions, questions, and explanations between concepts.  Use phrases like:
            *   "So, what does that actually mean?"
            *   "Now, let's move on to..."
            *   "Think of it like this..."
            *   "But here's the interesting part..."
            *   "Okay, that might sound a little complicated, so let's break it down."
            *   "You might be wondering..."
            *   "A good example of this is..."
            *   "In other words..."
            *   Add some interjection sounds such as "umm", "uh-ha", "wow", "ok".
        4.  For *every* major concept or step, include at least one "Why" question to prompt explanation of the underlying reasons or importance. Examples:
            *   "Why is this important?"
            *   "Why does this work?"
            *   "Why choose this method?"
            * "But why is that the case?"
        5.  Make the transcript feel like a real conversation, not just reading facts.
        6.  The transcript must be written in English.
        7.  Remove any code snippets and focus on the *explanation* of the concepts. If code is mentioned, give a *brief, high-level* description of what it does, *not* the code itself.
        8.  Start explaining with the question WHY.
        {'9. Continue from the previous part in a natural way.' if part_number > 0 else ''}
        {'10. End in a way that transitions to the next part.' if part_number < total_parts - 1 else ''}
        11. Keep sentences short and easy to understand.
        12. The format must be a conversational way, not instructure that focus for reading, no actual heading or subheading.
        13. Do not include the code snippets, but explain code flow and its component meaning.
        14. Do not use markdown, HTML, or any other formatting in the transcript. Please keep it plain text.
        15. Do not include any URLs or external references in the transcript.
        16. Convert numerical values to words (e.g., "5" becomes "five").

        Here is the source content to convert:
        -----------
        {content}
        -----------

        Begin the transcript now:
        """
    return prompt