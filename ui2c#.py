import json, xmltodict, sys, os

uiFilePath='./gui.ui'
outPutCSPath='./output.cs'

uiFile = json.loads(json.dumps(xmltodict.parse(open(uiFilePath, 'r', encoding='UTF-8').read())))
groupListIndex = []
frameListIndex = []
tabpageListIndex = []
tabcontrolListIndex = []

tabpageNameList = []
tabpageClassList = []
controlNameList = []
controlClassList = []

writeLine = []
f = open(outPutCSPath, 'w')
def loadjson(json):
    # 在最外面的QTabWidget处理
    if '@class' in json:
        if json['@class'] == 'QTabWidget':
            print(' [' + json['@class'] + '] ' + json['@name'] + ' -> ' + qtclasstocs(json['@class']))
            controlNameList.append(json['@name'])
            controlClassList.append(qtclasstocs(json['@class']))
            tabcontrolListIndex.append(len(json['widget']))
            tabpageClassList.append(json['@class'])
            tabpageNameList.append(json['@name'])
            tempcs = json2cs(json)
            if not tempcs is None:
                writeLine.append(tempcs)

    # widget列表,centralwidget第一级下可能不是列表类型，特殊处理
    if 'widget' in json:
        loadjson(json['widget'])

    for x in json:
        # widget列表
        if 'widget' in x:
            loadjson(x['widget'])

        if not '@name' in x:
            return
        else:
            controlNameList.append(x['@name'])

        if '@class' in x:
            print(' [' + x['@class'] + '] ' + x['@name'] + ' -> ' + qtclasstocs(x['@class']))
            controlClassList.append(qtclasstocs(x['@class']))
            if x['@class'] == 'QGroupBox':
                groupListIndex.append(len(x['widget']))
            elif x['@class'] == 'QFrame':
                frameListIndex.append(len(x['widget']))
            elif x['@class'] == 'QWidget':
                tabpageListIndex.append(len(x['widget']))
                tabpageNameList.append(x['@name'])
                tabpageClassList.append(x['@class'])

        tempcs=json2cs(x)
        if not tempcs is None:
            writeLine.append(tempcs)

def json2cs(json):
    objectName = json['@name']
    className = json['@class']
    if 'property' in json:

        if isinstance(json['property'], list):
            # 寻找rect
            for pro in json['property']:
                if 'rect' in pro:
                    property = pro['rect']
        else:
            property = json['property']['rect']

        # QPushButton,QLabel,QCheckBox处理
        if className == 'QPushButton' or className == 'QLabel' or className == 'QCheckBox' or className == "QLineEdit":
            text = ''
            for item in json['property']:
                if item['@name'] == "title" or item['@name'] == "text" or item['@name'] == 'placeholderText':
                    text = item['string']
            cs = '''
this.onm.Location = new System.Drawing.Point(%d, %d);
this.onm.Name = "onm";
this.onm.Size = new System.Drawing.Size(%d, %d);
this.onm.Text = "%s";
            '''.replace('onm', objectName) % (int(property['x']),
                   int(property['y']),
                   int(property['width']),
                   int(property['height']),
                   text
                )
            return cs
        elif className == 'QSpinBox':
            maximum = 0
            minimum = 0
            value = 0
            for item in json['property']:
                if item['@name'] == "maximum":
                    maximum = int(item['number'])
                elif item['@name'] == "minimum":
                    minimum = int(item['number'])
                    value = value if minimum > value else minimum
                elif item['@name'] == "value":
                    value = int(item['number'])
            cs = '''
    this.onm.Location = new System.Drawing.Point(%d, %d);
    this.onm.Name = "onm";
    this.onm.Size = new System.Drawing.Size(%d, %d);
    this.onm.Maximum = %i;
    this.onm.Minimum = %i;
    this.onm.Value = %i;
                '''.replace('onm', objectName) % (int(property['x']),
                                                  int(property['y']),
                                                  int(property['width']),
                                                  int(property['height']),
                                                  maximum,
                                                  minimum,
                                                  value
                                                  )
            return cs
        elif className == "QComboBox" or className == "QGroupBox" or className == "QFrame" or className == "QTableWidget":
            cs = '''
            this.onm.Location = new System.Drawing.Point(%d, %d);
            this.onm.Name = "onm";
            this.onm.Size = new System.Drawing.Size(%d, %d);
                        '''.replace('onm', objectName) % (int(property['x']),
                                                          int(property['y']),
                                                          int(property['width']),
                                                          int(property['height'])
                                                          )
            return cs
        elif className == "QTextBrowser":
            html = ''
            for item in json['property']:
                if item['@name'] == "html":
                    html = str(item['string']).replace('"', '""')
            cs = '''
            this.onm.Location = new System.Drawing.Point(%d, %d);
            this.onm.Name = "onm";
            this.onm.Size = new System.Drawing.Size(%d, %d);
            this.onm.DocumentText = @"%s";
                        '''.replace('onm', objectName) % (int(property['x']),
                                                          int(property['y']),
                                                          int(property['width']),
                                                          int(property['height']),
                                                          html
                                                          )
            return cs
        elif className == "QListWidget":
            items = []
            for item in json['item']:
                if item['property']['@name'] == "text":
                    items.append(item['property']['string'])
            items = str(items).replace('\'', '"')[1:-1]
            cs = '''
            this.onm.Location = new System.Drawing.Point(%d, %d);
            this.onm.Name = "onm";
            this.onm.Size = new System.Drawing.Size(%d, %d);
            this.onm.Items.AddRange(new object[] {%s});
                        '''.replace('onm', objectName) % (int(property['x']),
                                                          int(property['y']),
                                                          int(property['width']),
                                                          int(property['height']),
                                                          items
                                                          )
            return cs
        elif className == "QTabWidget":
            currentIndex = 0
            for item in json['property']:
                if item['@name'] == "currentIndex":
                    currentIndex = int(item['number'])
            cs = '''
            this.onm.Location = new System.Drawing.Point(%d, %d);
            this.onm.Name = "onm";
            this.onm.Size = new System.Drawing.Size(%d, %d);
            this.onm.SelectedIndex = %d;
                        '''.replace('onm', objectName) % (int(property['x']),
                                                          int(property['y']),
                                                          int(property['width']),
                                                          int(property['height']),
                                                          currentIndex
                                                          )
            return cs

def qtclasstocs(classname):
    if classname == "QPushButton":
        return "Button"
    elif classname == "QLabel":
        return "Label"
    elif classname == "QCheckBox":
        return "CheckBox"
    elif classname == "QSpinBox":
        return "NumericUpDown"
    elif classname == "QComboBox":
        return "ComboBox"
    elif classname == "QLineEdit":
        return "TextBox"
    elif classname == "QTextBrowser":
        return "WebBrowser"
    elif classname == "QTableWidget":
        return "DataGridView"
    elif classname == "QGroupBox":
        return "GroupBox"
    elif classname == "QFrame":
        return "Panel"
    elif classname == "QListWidget":
        return "ListBox"
    elif classname == "QTabWidget":
        return "TabControl"
    elif classname == "QWidget":
        return "TabPage"
    else:
        print('[Warning] Unsupport control "' + classname + '"')
        return classname[1:]

def initcontrol(name, classname):
    return "this.%s = new System.Windows.Forms.%s();" % (name, classname)

def regcontrol(name, classname):
    return "private System.Windows.Forms.%s %s;" % (classname, name)

def formregcontrol(name):
    return "this.Controls.Add(%s);" % name

for i in uiFile['ui']['widget']['widget']:
    print(i['@name'])
    if i['@class'] == 'QWidget':
        loadjson(i['widget'])

# 寻找Group
groupIndex = 0
for id,cl in enumerate(controlClassList):
    if cl == 'GroupBox':
        # 递归后顺序变反
        for x in range(-1, -groupListIndex[groupIndex]-1, -1):
            writeLine.append('\n'+
            "this.%s.Controls.Add(this.%s);" % (controlNameList[id], controlNameList[id+x]))
        groupIndex += 1

# 寻找Frame
frameIndex = 0
for id,cl in enumerate(controlClassList):
    if cl == 'Panel':
        for x in range(-1, -frameListIndex[frameIndex]-1, -1):
            writeLine.append('\n'+
            "this.%s.Controls.Add(this.%s);" % (controlNameList[id], controlNameList[id+x]))
        frameIndex += 1

# 寻找TabPage
tabpageIndex = 0
for id,cl in enumerate(controlClassList):
    if cl == 'TabPage':
        for x in range(-1, -tabpageListIndex[tabpageIndex]-1, -1):
            writeLine.append('\n'+
            "this.%s.Controls.Add(this.%s);" % (controlNameList[id], controlNameList[id+x]))
        tabpageIndex += 1

# 寻找TabControl
tabcontrolIndex = 0
for id,cl in enumerate(tabpageClassList):
    if cl == "QTabWidget":
        for x in range(1, tabcontrolListIndex[tabcontrolIndex]+1):
            writeLine.append('\n'+
            "this.%s.Controls.Add(this.%s);" % (tabpageNameList[id], tabpageNameList[id+x]))
        tabcontrolIndex += 1

# 窗口处理
uijson = uiFile['ui']['widget']
uiName = uiFile['ui']['widget']['@name']
for item in uijson['property']:
    if 'rect' in item:
        uiProperty = item['rect']
    elif item['@name'] == "windowTitle":
        windowTitle = str(item['string'])

writeLine.append('\n' + '''
this.ClientSize = new System.Drawing.Size(%d, %d);
this.Name = "%s";
this.Text = "%s";
            ''' % (int(uiProperty['width']),
                   int(uiProperty['height']),
                   uiName,
                   windowTitle
                  ))
# 注册所有控件到窗口
index = 0
for i in controlNameList:
    writeLine.append('\n' + formregcontrol(i))
    index += 1

# 写入

f.writelines('private void InitializeComponent()\n{')

# 注册所有控件
index = 0
for i in controlNameList:
    f.writelines('\n'+ initcontrol(i, controlClassList[index]))
    index += 1

for line in writeLine:
    f.writelines(line)

f.writelines('\n}')

# 注册所有控件
index = 0
for i in controlNameList:
    f.writelines('\n'+ regcontrol(i, controlClassList[index]))
    index += 1

f.close()
