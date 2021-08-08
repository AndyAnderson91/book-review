def get_pagination_numbers(cur_page, total_pages):
    if total_pages < 7:
        sep_first = False
        mid_nums = list(range(1, total_pages+1))
        sep_last = False

    else:
        if cur_page < 4:
            sep_first = False
            mid_nums = list(range(1, 6))
            sep_last = True
        elif cur_page > total_pages - 3:
            sep_first = True
            mid_nums = list(range(total_pages-4, total_pages+1))
            sep_last = False
        else:
            sep_first = True
            mid_nums = list(range(cur_page-2, cur_page + 3))
            sep_last = True

    numbers = {
        'sep_first': sep_first,
        'mid_nums': mid_nums,
        'sep_last': sep_last,
    }

    return numbers

