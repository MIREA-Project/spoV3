from aiogram import Router

from .commands_handler import command_router

# union routers
router_main: Router = Router()
router_main.include_router(command_router)
