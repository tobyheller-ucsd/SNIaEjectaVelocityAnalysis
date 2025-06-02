def progress_bar(completion: float, length: int, suffix=''):
    end = '\r'
    if completion == 1:
        end = '\n'
    print(f'{completion: .2%} |{''.join([chr(0x2588) if (i/length < completion) else ' ' for i in range(length)])}|{suffix}', end=end)