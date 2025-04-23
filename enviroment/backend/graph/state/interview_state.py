from typing import TypeDict

class GraphState(TypeDict):
    interview_id:        str
    user_id:             str
    comany_code:         str
    job_code:            str
    person_exp:          str
    question_list:       List[str]
    answer_list:         List[str]
    answer_example_list: List[str]
    overall_review:      str
    area_score_one:      int
    area_score_two:      int
    area_score_three:    int
    answer_logic:        str
    q_comp:              str
    hab_chk:             str
    job_exp:             str
    time_mgmt:           str
    video_path:          str
