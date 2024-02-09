import pandas as pd
import math

product = 'Grille'
width = 3000
length = 2000
pitch = 45
allowed_wastage = 100
horizontal = True
carrier_max_gap = 900
carrier_end_gap = 150


def calculate_num_pieces(product, width, length, pitch, horizontal):

    num_pieces = math.ceil(length / pitch)

    if horizontal == False:
        temp = width
        width = length
        length = temp
    
    assert width >= 150
    assert pitch < length

    print(num_pieces, product, 'pieces required')

    return num_pieces


def filter_inv(df, product):#, num_pieces):
    inv = df[(df['name'] == product)]# & (df['stock'] >= num_pieces)]
    return inv


def find_counts(df):
    counts = {}
    for _, row in df.iterrows():
        if int(row['length']) not in counts:
            counts[row['length']] = 0
        counts[row['length']] += row['stock']
    
    return counts


def find_combinations_grille(target, lengths, counts, wastage):
    output = set()
    
    def dfs(total, arr, i):
        if target <= total <= target + wastage:
            stock_avail = True
            for l in set(arr):
                req = arr.count(l) * num_pieces
                if counts[l] < req:
                    stock_avail = False
                    break
            if stock_avail:
                output.add(tuple(sorted(arr)))
            return
        
        if (total > target + wastage) or (i >= len(lengths)):
            return
        
        arr.append(lengths[i])
        dfs(total + lengths[i], arr, i)
        arr.pop()
        dfs(total, arr, i + 1)
    
    dfs(0, [], 0)
    return [list(x) for x in output]


def find_combinations_grille(target, lengths, counts, req_pieces, wastage):
    output = set()
    
    def dfs(total, arr, i):
        if target <= total <= target + wastage:
            stock_avail = True
            for l in set(arr):
                req = arr.count(l) * req_pieces
                if counts[l] < req:
                    stock_avail = False
                    break
            if stock_avail:
                output.add(tuple(sorted(arr)))
            return
        
        if (total > target + wastage) or (i >= len(lengths)):
            return
        
        arr.append(lengths[i])
        dfs(total + lengths[i], arr, i)
        arr.pop()
        dfs(total, arr, i + 1)
    
    dfs(0, [], 0)
    return [list(x) for x in output]


def carrier_calculation(
    carrier_max_gap,
    carrier_end_gap,
    length_combination,
    carrier_lengths,
    carriers_per_grille,
    carrier_distances
):
    for l in length_combination:
        carrier_lengths = 1 # for end piece
        centre_width = l - (2 * carrier_end_gap)
        if centre_width >= 900:
            carrier_lengths += math.ceil(centre_width / carrier_max_gap)
            centre_gap = centre_width / (carrier_lengths - 1)
        else:
            carrier_lengths += 1
            centre_gap = centre_width
        carriers_per_grille.append(carrier_lengths)

        distances = []
        curr = 0
    
    for i in range(carrier_lengths):
        if i == 0:
            curr += carrier_end_gap
        else:
            curr += centre_gap
        distances.append(curr)
    carrier_distances.append(distances)

    print('For the chosen option, we will need to place carriers as below: ')
    print('Number of {len} mm length carriers needed: {num}'.format(len=length, num=sum(carriers_per_grille)))
    print('Cumulative carrier distance breakdown for each individual {p} piece chosen: '.format(p=product))

    for i in range(len(length_combination)):
        print('{len}: {d}'.format(len=length_combination[i], d=carrier_distances[i]))

    return carrier_distances


if __name__ == '__main__':

    inventory = pd.read_csv('inventory.csv')
    print(inventory)

    num_pieces = calculate_num_pieces(product, width, length, pitch, horizontal)
    curr_inv = filter_inv(inventory, 'Grille')#, num_pieces)
    cnts = find_counts(curr_inv)
    possible_lengths = find_combinations_grille(width, curr_inv['length'].unique().tolist(), cnts, num_pieces, allowed_wastage)

    for opt in range(len(possible_lengths)):
        print('Option {num}: {option}'.format(num=opt + 1, option=possible_lengths[opt]))
        print('Wastage: {}'.format(sum(possible_lengths[opt])-width))
        print('total: {}\n'.format(sum(possible_lengths[opt])))

    print('Enter the option number you want to choose.')

    option = 0
    length_combination = possible_lengths[option]
    carrier_lengths = 0
    carriers_per_grille = []
    
    carrier_distances = carrier_calculation(
        carrier_max_gap,
        carrier_end_gap,
        length_combination,
        carrier_lengths,
        carriers_per_grille,
        []
    )

    print(carrier_distances[option])
