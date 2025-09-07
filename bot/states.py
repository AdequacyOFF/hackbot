from aiogram.fsm.state import State, StatesGroup

class ApplyStates(StatesGroup):
    choosing_comp = State()
    confirm_comp = State()
    team_name = State()
    team_size = State()
    member_rank = State()
    member_fio = State()
    member_group = State()
    captain = State()
    location = State()
    curator = State()

class ResultsStates(StatesGroup):
    picking_team = State()
    place = State()
    presentation = State()
    repo = State()
    comment = State()

class SuggestStates(StatesGroup):
    title = State()
    sponsor = State()
    dates = State()
    format = State()
    link = State()

class AdminStates(StatesGroup):
    menu = State()
    add_title = State()
    add_sponsor = State()
    add_dates = State()
    add_format = State()
    add_link = State()