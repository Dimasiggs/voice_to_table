import Commands
import pandas as pd

def run_commands(commands_list, table: pd.DataFrame = None) -> pd.DataFrame:
    for command_data in commands_list:
        command = command_data.get("command")
        args = command_data.get("args", {})

        match command:
            case "copy":
                Commands.copy(table, args)
            case "paste":
                Commands.paste(table, args)
            case "moveto":
                Commands.moveto(table, args)
            case "delete":
                Commands.delete(table, args)
            case "create":
                Commands.create(table, args)
            case "write":
                Commands.write(table, args)
            case "right":
                Commands.right(table, args)
            case "left":
                Commands.left(table, args)
            case "up":
                Commands.up(table, args)
            case "down":
                Commands.down(table, args)
            case "date":
                Commands.date(table, args)
            case "create_columns":
                Commands.create_columns(table, args)
            case "create_table":
                table = Commands.create_table(table, args)
            case _:
                raise ValueError(f"Неизвестная команда: {command}")
    
    return table