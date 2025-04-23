from utils.backend import Backend


class Mock_interview(Backend):
    def __init__(self):
        super().__init__()
    
    def get_company_list(self):
        URL = '/mock/itv/get_company_list'
        result = self.req_get(URL)
        print(result)
        return result
    
    def get_job_list(self):
        URL = '/mock/itv/get_job_list'
        result = self.req_get(URL)
        print(result)
        return result