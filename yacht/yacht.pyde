class Dice():
    def __init__(self, x, y):
        self.side = int(random(1, 7))
        self.x = x
        self.y = y
        self.status = 'stopped' # rolling
        self.last_rolled = millis()
        self.keep = False
        
    def roll(self):
        if self.status != 'rolling' and not self.keep:
            self.status = 'rolling'
            self.last_rolled = millis()
            
    def translate(self, dst_x, dst_y):
        dx = int((dst_x - self.x) / 4)
        dy = int((dst_y - self.y) / 4)
        
        if dx == 0:
            self.x = dst_x
        else:
            self.x += dx
        if dy == 0:
            self.y = dst_y
        else:
           self.y += dy
        
    def display(self):
        if self.status == 'rolling':
            if millis() - self.last_rolled > random(1000, 3000):
                self.status = 'stopped'

            self.side = int(random(1, 7))
            
            self.x += int(random(-10, 10))
            self.y += int(random(-10, 10))
            
            self.x = max(50, self.x)
            self.y = max(50, self.y)

        if self.keep:
            strokeWeight(5)
            stroke(204, 102, 0)
        else:
            noStroke()

        for i in range(1, 10, 2):
            fill(0, 100 - 5 * (i + 1))
            rectMode(CENTER)
            rect(self.x + i, self.y + i, 100, 100)

        fill('#ffffff')
        rectMode(CENTER)
        rect(self.x, self.y, 100, 100)
        
        noStroke()
        fill('#333333')
        if self.side == 1 or self.side == 3 or self.side == 5:
            ellipse(self.x, self.y, 20, 20)
        if self.side == 4 or self.side == 5 or self.side == 6:
            ellipse(self.x - 30, self.y - 30, 20, 20)
        if self.side == 6:
            ellipse(self.x - 30, self.y, 20, 20)
        if self.side == 2 or self.side == 3 or self.side == 4 or self.side == 5 or self.side == 6:
            ellipse(self.x - 30, self.y + 30, 20, 20)
        if self.side == 2 or self.side == 3 or self.side == 4 or self.side == 5 or self.side == 6:
            ellipse(self.x + 30, self.y - 30, 20, 20)
        if self.side == 6:
            ellipse(self.x + 30, self.y, 20, 20)
        if self.side == 4 or self.side == 5 or self.side == 6:
            ellipse(self.x + 30, self.y + 30, 20, 20)
            
class Strategy():
    def __init__(self, strategies):
        self.strategies = strategies
        
    def set_dices(self, dices):
        self.dices = dices
        
    def calculate(self):
        self.sides = [dice.side for dice in self.dices]
        self.unique = set(self.sides)
        
        upper_score = 0
        for i in range(1, 7):
            if self.strategies['%ds' % i]['done']:
                continue

            score = self.sum_of_single(i)
            self.strategies['%ds' % i]['score'] = score
            upper_score += score
            
        if upper_score >= 63:
            self.strategies['Bonus']['score'] = 35

        if not self.strategies['Choice']['done']:
            self.strategies['Choice']['score'] = sum(self.sides)
        if not self.strategies['3-of-a-kind']['done']:
            self.strategies['3-of-a-kind']['score'] = self.of_a_kind(3)
        if not self.strategies['4-of-a-kind']['done']:
            self.strategies['4-of-a-kind']['score'] = self.of_a_kind(4)
        if not self.strategies['Full House']['done']:
            self.strategies['Full House']['score'] = self.full_house()
        if not self.strategies['S. Straight']['done']:
            self.strategies['S. Straight']['score'] = self.small_straight()
        if not self.strategies['L. Straight']['done']:
            self.strategies['L. Straight']['score'] = self.large_straight()
        if not self.strategies['Yacht']['done']:
            self.strategies['Yacht']['score'] = self.of_a_kind(5)
            
        self.strategies['Total']['score'] = 0
        for k, v in self.strategies.items():
            if v['done']:
                self.strategies['Total']['score'] += v['score']
        
        return self.strategies
        
    def count(self, number):
        return len([side for side in self.sides if side == number])
    
    def highest_repeated(self, min_repeats):
        repeats = [x for x in self.unique if self.count(x) >= min_repeats]
        return max(repeats) if repeats else 0
    
    def of_a_kind(self, n):
        hr = self.highest_repeated(n)
        
        if hr == 0:
            return 0
        
        if n == 5:
            return 50
        
        rests = [side for side in self.sides if side != hr]

        return hr * n + sum(rests)
    
    def sum_of_single(self, number):
        return sum([x for x in self.sides if x == number])
    
    def full_house(self):
        hr = self.highest_repeated(3)
        if hr > 0:
            rests = [side for side in self.sides if side != hr]
            if len(set(rests)) == 1 and len(rests) == 2:
                return 25
            
        hr = self.highest_repeated(2)
        if hr > 0:
            rests = [side for side in self.sides if side != hr]
            if len(set(rests)) == 1 and len(rests) == 3:
                return 25

        return 0
    
    def small_straight(self):
        if set([1, 2, 3, 4]).issubset(self.unique) or set([2, 3, 4, 5]).issubset(self.unique) or set([3, 4, 5, 6]).issubset(self.unique):
            return 30
        return 0
    
    def large_straight(self):
        if set([1, 2, 3, 4, 5]).issubset(self.unique) or set([2, 3, 4, 5, 6]).issubset(self.unique):
            return 40
        return 0
    
class GameManager():
    def __init__(self):
        self.set_status('normal')
        self.n_rolling_dices = 0
        self.n_rolls = 0
        self.n_keeps = 0
        self.score = 0
        self.n_rounds = 1
        self.highest_score = 0
        
    def reset(self):
        self.set_status('normal')
        self.n_rolling_dices = 0
        self.n_rolls = 0
        self.n_keeps = 0
        self.score = 0
        
        for dice in dices:
            dice.keep = False
        
        if self.n_rounds == 13:
            self.reset2()
        else:
            self.n_rounds += 1
        
    def reset2(self):
        self.n_rounds = 1
        self.highest_score = strategies['Total']['score']
        
        for k, v in strategies.items():
            strategies[k]['done'] = False

    def set_status(self, status):
        self.status = status # (normal, rolling, sorting, keeping, calculating)
        self.last_status_changed = millis()
        
    def roll_dices(self):
        if self.n_keeps < 5:
            self.set_status('rolling')
            self.n_rolls += 1
    
            for dice in dices:
                dice.roll()
        else:
            self.set_status('calculating')
            
    def print_board(self, strategies):
        textSize(32)
        textAlign(LEFT)
    
        for k, strategy in strategies.items():
            if strategy['selected']:
                fill(0, 255, 255)
            elif strategy['done']:
                fill(150)
            else:
                fill(240)
            text('%s' % (k,), strategy['position'][0], strategy['position'][1])
            text('%2d' % (strategy['score'],), strategy['position'][0] + 300, strategy['position'][1])
            
    def print_status(self):
        status_map = {
            'normal': 'Roll dices',
            'rolling': '',
            'sorting': '',
            'keeping': 'Select dices',
            'calculating': 'Choose category'     
        }

        fill(240)
        textSize(32)
        textAlign(CENTER)
        text(status_map[self.status], 500, 100)
        
        textAlign(RIGHT)
        text('Round %d/13' % (self.n_rounds), 980, 40)
        text('%d/3' % (self.n_rolls), 980, 80)
        
        textAlign(LEFT)
        text('Highest %d' % (self.highest_score), 10, 40)

# main
strategies_order = ['1s', '2s', '3s', '4s', '5s', '6s', 'Bonus', 'Choice', '3-of-a-kind', '4-of-a-kind', 'Full House', 'S. Straight', 'L. Straight', 'Yacht', 'Total']
strategies = {
    '1s': 0,
    '2s': 0,
    '3s': 0,
    '4s': 0,
    '5s': 0,
    '6s': 0,
    'Bonus': 0,
    'Choice': 0,
    '3-of-a-kind': 0,
    '4-of-a-kind': 0,
    'Full House': 0,
    'S. Straight': 0,
    'L. Straight': 0,
    'Yacht': 0,
    'Total': 0
}

for i, strategy_name in enumerate(strategies_order):
    strategies[strategy_name] = {
           'position': [300, 400 + i * 40],
           'score': 0,
           'selected': False,
           'done': False
    }

gm = GameManager()
strategy = Strategy(strategies)

dices = []
init_pos = [
    (200, 200),
    (350, 200),
    (500, 200),
    (650, 200),
    (800, 200)
]

for pos in init_pos:
    dice = Dice(pos[0], pos[1])
    dices.append(dice)

def setup():
    frameRate(30)
    size(1000, 1000)

def draw():
    global init_pos, strategy

    background('#777777')
    
    gm.n_rolling_dices = 0
    gm.n_keeps = 0

    for i, dice in enumerate(dices):
        dice.display()
        
        if dice.status == 'rolling':
            gm.n_rolling_dices += 1
            
        if dice.keep:
            gm.n_keeps += 1
        
    if gm.status == 'rolling' and gm.n_rolling_dices == 0:
        gm.set_status('sorting')
    elif gm.status == 'sorting':
        dices.sort(key=lambda x: x.side, reverse=False)

        for dice, pos in zip(dices, init_pos):
            dice.translate(pos[0], pos[1])
    
        if millis() - gm.last_status_changed > 1000:
            if gm.n_rolls >= 3 or gm.n_keeps >= 5:
                gm.set_status('calculating')
            else:
                gm.set_status('keeping')

    strategy.set_dices(dices)
    strategy.calculate()

    gm.print_board(strategies)
    gm.print_status()
    
def mouseReleased():
    # dices area
    for i, pos in enumerate(init_pos):
        if pos[0] - 50 < mouseX < pos[0] + 50 and pos[1] - 50 < mouseY < pos[1] + 50:
            if gm.status == 'keeping':
                dices[i].keep = not dices[i].keep
                break
    
    # score board area
    if 300 < mouseX < 640 and strategies[strategies_order[0]]['position'][1] - 30 < mouseY < strategies[strategies_order[-1]]['position'][1]:
        if gm.status == 'keeping' or gm.status == 'calculating':
            for k, v in strategies.items():
                if k == 'Bonus' or k == 'Total':
                    continue

                pos = v['position']
                if 300 < mouseX < 640 and pos[1] - 30 < mouseY < pos[1] + 10 and strategies[k]['done'] == False:
                    strategies[k]['selected'] = not strategies[k]['selected']
                else:
                    strategies[k]['selected'] = False
    
    # background area
    elif not (init_pos[0][0] - 50 < mouseX < init_pos[-1][0] + 50 and init_pos[0][1] - 50 < mouseY < init_pos[-1][1] + 50):
        selected = None

        for k, v in strategies.items():
            if v['selected']:
                selected = k
                
        if selected is not None:
            if gm.status == 'keeping' or gm.status == 'calculating':
                strategies[selected]['done'] = True
                strategies[selected]['selected'] = False
                selected = None
                gm.reset()
        else:
            if gm.status == 'keeping' or gm.status == 'normal':
                gm.roll_dices()
            elif gm.status == 'calculating':
                if selected is not None:
                    strategies[selected]['done'] = True
                    strategies[selected]['selected'] = False
                    selected = None
                    gm.reset()

    
