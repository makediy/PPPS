import picoweb
import tryi2c
import time
import ujson

app = picoweb.WebApp(None)
def webpage():
    
    htmlContent =     """<!DOCTYPE html> <meta charset="UTF-8"><head><script src="static/jquery.min.js"></script>
    <title>PPPS网页控制界面</title> <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
      h1{color: #0F3333; padding: 2vh;style="line-height: 1em;}p{font-size: 1rem;style="line-height: 1em;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
      border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 2rem; margin: 2px; cursor: pointer;}
.button2{background-color: #4286f4;font-size: 1rem;}input{ font-size: 1rem;}</style>
    
      </head><body>  <img src='static/ppps.png' width="128" height="128"><br />
	   <h1><font color="red">PPPS网页控制界面</font></h1>
     
      <blockquote>
        <blockquote>
          </blockquote>
        <table width="300" border="0" align="center">
          <tr>
            <td width="100"><p>输入电压:</p></td>
            <td width="100" bordercolor="#FFFFFF"><p><strong><span id="votage_in" value=0>0</span></strong></p></td>
            <td width="100">&nbsp;</td>
          </tr>
          <tr>
            <td><p>输出电压:</p></td>
            <td bordercolor="#FFFFFF"><p><strong><span id="votage" value=0>0</span></strong></p></td>
            <td>&nbsp;</td>
          </tr>
          <tr>
            <td><p>输出电流:</p></td>
            <td bordercolor="#FFFFFF"><p><strong><span id="current">0 </span></strong></p></td>
            <td>&nbsp;</td>
          </tr>
          <tr>
            <td><p>电压设置:</p></td> 
            <td bordercolor="#FFFFFF"><p><strong><span id="votage_set">0</span></strong></p></td>
            <td><input name="text" type="text" class="txt" id="votage_set_input" onKeyUp="this.value=this.value.replace(/[^0-9\.]/g,'')" value="0" size="8" maxlength="4" ></td>
          </tr>
          <tr>
            <td><p>电流设置:</p></td>
            <td bordercolor="#FFFFFF"><p><strong><span id="current_set">0</span></strong></p></td>
            <td><input name="text2" type="text" class="txt" id="current_set_input" onKeyUp="this.value=this.value.replace(/[^0-9\.]/g,'')" value="0" size="8" maxlength="4" ></td>
          </tr>
        </table>
        <p>
          <button class="button" type="submit" name="btn" id="btn"  onclick="generate();return false">
          <div align="center">发送</div>
          </button>
          </br>
        </p>
      </blockquote>
      <p><img src='static/logo.png'></p>
      <script> 
var votage_in = document.getElementById("votage_in");
var votage = document.getElementById("votage");
var current = document.getElementById("current");
var votage_set = document.getElementById("votage_set");
var current_set = document.getElementById("current_set");
var current_set_input = document.getElementById("current_set_input")
var votage_set_input = document.getElementById("votage_set_input")
var btn = document.getElementById("btn")
btn
let num = 0
var timer = setInterval(function() {
	num++;
	btn.innerText='发送';
    $.ajax({
        url : "/getdata",
        type : "POST",
        datatype : "JSON",
            success:function(datas){     
                votage_in.innerText= datas.votage_in;
                votage.innerText= datas.votage;
                current.innerText= datas.current;
                votage_set.innerText= datas.votage_set;
                current_set.innerText= datas.current_set;
                
                
        }
    })

},500)
function generate() {
    fetch("/", {
        method: "POST",
        body: JSON.stringify({
            votage_set_input :votage_set_input.value,
            current_set_input :current_set_input.value,
        }),
        headers: {
          'Content-Type': 'Content-Length'
        },        
    });
    btn.innerText="下发成功！"
}


</script>
      </body></html>"""
    return htmlContent



@app.route('/getdata',methods=['GET', 'POST'])
def return_data(req, resp):
    print('return data')
    
    votage_in=str(round(tryi2c.aVin.read_uv()/1000000.0*11,2))
    print (votage_in)
    votage=str(round(tryi2c.aVout.read_uv()/1000000.0*11,2))
    current=str(round(tryi2c.aIout.read_uv()/1000.0*2/640,2))
    current_set=str(round(tryi2c.sc.IOUT_ILIM,2))
    votage_set=str(round(tryi2c.sc.VOUT_SET,2))
    jsonData = {"votage":votage,"current":current,"votage_set":votage_set,"votage_in":votage_in,"current_set":current_set}
    encoded = ujson.dumps(jsonData)

    yield from picoweb.start_response(resp, content_type = "application/json")
    yield from resp.awrite(encoded)

@app.route("/")
def index(req, resp):
    if req.method == 'POST':
        #print('1111')
        size = int(req.headers[b"Content-Length"])
        #print(size)
        data = yield from req.reader.readexactly(size)
        #print(data)        
        form=ujson.loads(data)
        #print('1111',form)
        votage_set_input = float(form["votage_set_input"])
        current_set_input=float(form["current_set_input"])
        print(votage_set_input,current_set_input)
        if votage_set_input<=4:
            level=0
        elif votage_set_input<=8:
            level=1
        elif votage_set_input<=11:
            level=2
        elif votage_set_input<=14:
            level=3
        else:level=4
#         print(level)
#         tryi2c.SET_INPUT_LEVEL(level)
        tryi2c.sc.Output_Voltage_Setting(votage_set_input)
        tryi2c.sc.Output_Current_Limit(current_set_input)
    else:
        yield from picoweb.start_response(resp,content_type = "text/html")
        yield from resp.awrite(webpage()) 
level=0

 
