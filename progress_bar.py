def progress_bar(completed: float, total: float, length: int, suffix=''):
    end = '\r'
    if total == 1:
        end = '\n'
    print(f'{(completed / total): .2%} - {completed}/{total} |{''.join([chr(0x2588) if (i/length < completed/total) else ' ' for i in range(length)])}|{suffix}', end=end)