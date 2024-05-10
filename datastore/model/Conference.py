class Conference:
    def __init__(self, _id, created_at, updated_at, name, location, start_date, end_date, website, description=''):
        self.id = _id
        self.created_at = created_at
        self.updated_at = updated_at
        self.name = name
        self.location = location
        self.start_date = start_date
        self.end_date = end_date
        self.website = website
        self.description = description
