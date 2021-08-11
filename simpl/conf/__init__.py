from .app_settings import AppSettings


class Settings(AppSettings):
    SIMPL_CHARACTER = "simpl.Character"
    SIMPL_GAME_EXPERIENCE = "simpl.GameExperience"
    SIMPL_INSTANCE = "simpl.Instance"


settings = Settings()
