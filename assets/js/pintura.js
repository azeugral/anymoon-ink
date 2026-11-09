/* Anymoon — o retrato se pinta: pinceladas curvas que seguem o fluxo da imagem (WebGL2).
   pinturaHero(canvas) -> { carregar(bin, meta, foto), quadro(t, W, H, dpr, rect), ok } */
(function () {
  const VEL = 1.35;  /* 4,9 s -> 3,6 s */
  const VS = `#version 300 es
  precision highp float;
  layout(location=0) in vec4 aA;   // p0.xy p1.xy (normalizado)
  layout(location=1) in vec4 aB;   // p2.xy largura t0
  layout(location=2) in uvec2 aC;  // cor + camada
  uniform float uT, uPad, uN, uWmax, uTmax;
  out vec2 vUV; out vec3 vCor; out float vPr, vSem, vCam;
  vec2 bez(vec2 a, vec2 b, vec2 c, float u){ float k=1.-u; return k*k*a+2.*k*u*b+u*u*c; }
  vec2 dbez(vec2 a, vec2 b, vec2 c, float u){ return 2.*(1.-u)*(b-a)+2.*u*(c-b); }
  void main(){
    float esc = uN + 2.*uPad;
    vec2 p0 = aA.xy*esc-uPad, p1 = aA.zw*esc-uPad, p2 = aB.xy*esc-uPad;
    float w = aB.z*uWmax, t0 = aB.w*uTmax;
    float cam = float(aC.y >> 8u);
    float dur = .30 + .05*(5.-cam);
    float pr = clamp((uT - t0)/dur, 0., 1.);
    pr = 1. - pow(1.-pr, 2.4);
    int i = gl_VertexID/2; float lado = float(gl_VertexID%2)*2.-1.;
    float u = float(i)/10.;
    float us = u*pr;
    vec2 p = bez(p0,p1,p2,us), d = normalize(dbez(p0,p1,p2,us)+1e-5), n = vec2(-d.y,d.x);
    float corpo = .62 + .38*sqrt(sin(3.14159*clamp(u,.02,.98)));
    p += n*lado*w*.5*corpo;
    if (pr <= 0.) p = vec2(-9999.);
    gl_Position = vec4(p/uN*2.-1., 0., 1.); gl_Position.y = -gl_Position.y;
    vUV = vec2(us, lado); vPr = pr;
    vCor = vec3(float(aC.x & 255u), float(aC.x >> 8u), float(aC.y & 255u))/255.;
    vSem = fract(sin(dot(aA.xy+aB.xy, vec2(127.1,311.7)))*43758.5453);
    vCam = cam;
  }`;
  const FS = `#version 300 es
  precision highp float;
  in vec2 vUV; in vec3 vCor; in float vPr, vSem, vCam;
  out vec4 o;
  float h(float x){ return fract(sin(x*91.345)*47453.5453); }
  float vn(float x){ float i=floor(x), f=fract(x); f=f*f*(3.-2.*f); return mix(h(i),h(i+1.),f); }
  float vn2(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
    float a=h(i.x+i.y*57.), b=h(i.x+1.+i.y*57.), c=h(i.x+(i.y+1.)*57.), d=h(i.x+1.+(i.y+1.)*57.);
    return mix(mix(a,b,f.x),mix(c,d,f.x),f.y); }
  void main(){
    float s = vUV.x, v = vUV.y, sem = vSem*100.;
    float fr = 15. + 10.*vSem;
    float cer = vn(v*fr + sem)*.6 + vn(v*fr*2.3 + sem*1.7)*.4;              // cerdas
    float cer2 = vn2(vec2(v*fr*1.6 + sem, s*3.)) ;
    float borda = 1. - smoothstep(.70 - .25*cer, 1.0, abs(v));
    float ini = smoothstep(0., .05 + .10*cer2, s);
    float fim = smoothstep(vPr, vPr - .06 - .16*cer2, s);
    float seca = smoothstep(.55, 1., s) * (.35 + .25*vSem);                  // tinta acabando no fim do traco
    float a = borda*ini*fim*(1. - seca*step(cer, .42));
    if (a < .01) discard;
    float rel = vn(v*fr + sem + .35) - vn(v*fr + sem - .35);                 // relevo das cerdas (luz de cima)
    vec3 c = vCor*(.90 + .18*cer) + rel*.045 + (1.-smoothstep(0.,.25,s))*.025;
    a = min(1., a*1.05);
    o = vec4(c*a, a);
  }`;
  const VQ = `#version 300 es
  in vec2 p; out vec2 uv; uniform vec4 uR; uniform vec2 uV;
  void main(){ uv = p*.5+.5; vec2 q = uR.xy + uv*uR.zw; gl_Position = vec4(q/uV*2.-1., 0., 1.); gl_Position.y=-gl_Position.y; uv.y = uv.y; }`;
  const FQ = `#version 300 es
  precision highp float;
  in vec2 uv; out vec4 o;
  uniform sampler2D uTex, uFoto; uniform float uF, uT;
  float h2(vec2 p){ return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453); }
  float vn(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
    return mix(mix(h2(i),h2(i+vec2(1,0)),f.x),mix(h2(i+vec2(0,1)),h2(i+1.),f.x),f.y); }
  float fbm(vec2 p){ return vn(p)*.55 + vn(p*2.1+3.1)*.28 + vn(p*4.3+7.7)*.17; }
  void main(){
    vec4 c = texture(uTex, vec2(uv.x, 1.-uv.y));
    vec2 q = uv;
    /* aguada de base: a cor borrada floresce no papel antes das pinceladas */
    float ov = length((q - vec2(.5,.49))/vec2(.425,.435)) + (fbm(q*5.)-.5)*.32 + (fbm(q*19.)-.5)*.1;
    float cresce = clamp(uT/1.6, 0., 1.);
    float lim = .25 + .68*(1. - pow(1.-cresce, 2.));
    float ag = smoothstep(lim, lim - .07, ov) * .78;
    float franja = smoothstep(lim - .02, lim - .045, ov) - smoothstep(lim - .045, lim - .12, ov);   // borda escura da aquarela
    vec3 base = textureLod(uFoto, q, 6.5).rgb;
    base = mix(vec3(dot(base, vec3(.3,.59,.11))), base, .85) * (1. - franja*.12);
    vec4 fundo = vec4(base*ag, ag);
    c = c + fundo*(1. - c.a);
    float rosto = clamp(1.3 - length((q - vec2(.43,.31))/vec2(.16,.20)), 0., 1.);
    rosto = max(rosto, .8*clamp(1.2 - length((q - vec2(.52,.47))/vec2(.11,.18)), 0., 1.));
    vec3 f = texture(uFoto, uv).rgb;
    float m = uF*smoothstep(0.,1.,rosto)*c.a;
    vec3 cor = mix(c.rgb, f*c.a, m*.7);
    o = vec4(cor, c.a);
  }`;
  function sh(gl, t, s) { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o); if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw gl.getShaderInfoLog(o); return o; }
  function prog(gl, v, f) { const p = gl.createProgram(); gl.attachShader(p, sh(gl, gl.VERTEX_SHADER, v)); gl.attachShader(p, sh(gl, gl.FRAGMENT_SHADER, f)); gl.linkProgram(p); if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw gl.getProgramInfoLog(p); return p; }

  window.pinturaHero = function (cv, op) {
    op = op || {};
    const gl = cv.getContext('webgl2', { premultipliedAlpha: true, alpha: true, antialias: true, preserveDrawingBuffer: !!op.guardar });
    if (!gl) return { ok: false };
    const P = prog(gl, VS, FS), Q = prog(gl, VQ, FQ);
    const U = n => gl.getUniformLocation(P, n), UQ = n => gl.getUniformLocation(Q, n);
    let n = 0, meta = null, vao = null, fb = null, tex = null, foto = null, lado = 0;
    const qv = gl.createVertexArray(); gl.bindVertexArray(qv);
    const qb = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, qb);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
    function alvo(px) {
      if (px === lado) return; lado = px;
      if (!tex) { tex = gl.createTexture(); fb = gl.createFramebuffer(); }
      gl.bindTexture(gl.TEXTURE_2D, tex);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, px, px, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      gl.bindFramebuffer(gl.FRAMEBUFFER, fb); gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
    }
    const api = {
      ok: true, gl,
      carregar(buf, m, img) {
        meta = m; n = m.n;
        vao = gl.createVertexArray(); gl.bindVertexArray(vao);
        const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, buf, gl.STATIC_DRAW);
        gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 4, gl.UNSIGNED_SHORT, true, 20, 0); gl.vertexAttribDivisor(0, 1);
        gl.enableVertexAttribArray(1); gl.vertexAttribPointer(1, 4, gl.UNSIGNED_SHORT, true, 20, 8); gl.vertexAttribDivisor(1, 1);
        gl.enableVertexAttribArray(2); gl.vertexAttribIPointer(2, 2, gl.UNSIGNED_SHORT, 20, 16); gl.vertexAttribDivisor(2, 1);
        foto = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, foto);
        gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
        gl.generateMipmap(gl.TEXTURE_2D);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
      },
      /* t em segundos; rect = [x, y, lado] em px CSS; fundo = cor rgb do papel (ou null = transparente) */
      quadro(t, W, H, dpr, rect, fundo) {
        if (!meta) return;
        t *= VEL;  /* acelera a pintura inteira sem regerar as pinceladas */
        const cw = Math.round(W * dpr), ch = Math.round(H * dpr);
        if (cv.width !== cw || cv.height !== ch) { cv.width = cw; cv.height = ch; }
        const px = Math.min(4096, Math.round(rect[2] * dpr * (op.super || 1.5)));
        alvo(px);
        gl.bindFramebuffer(gl.FRAMEBUFFER, fb); gl.viewport(0, 0, px, px);
        gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
        gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
        gl.useProgram(P);
        gl.uniform1f(U('uT'), t); gl.uniform1f(U('uPad'), meta.pad); gl.uniform1f(U('uN'), meta.N);
        gl.uniform1f(U('uWmax'), meta.wmax); gl.uniform1f(U('uTmax'), meta.tmax);
        gl.bindVertexArray(vao);
        gl.drawArraysInstanced(gl.TRIANGLE_STRIP, 0, 22, n);
        gl.bindTexture(gl.TEXTURE_2D, tex); gl.generateMipmap && 0;
        gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.viewport(0, 0, cw, ch);
        if (fundo) gl.clearColor(fundo[0] / 255, fundo[1] / 255, fundo[2] / 255, 1); else gl.clearColor(0, 0, 0, 0);
        gl.clear(gl.COLOR_BUFFER_BIT);
        gl.useProgram(Q);
        gl.uniform4f(UQ('uR'), rect[0] * dpr, rect[1] * dpr, rect[2] * dpr, rect[2] * dpr); gl.uniform2f(UQ('uV'), cw, ch);
        const f = Math.min(1, Math.max(0, (t - meta.fim) / 1.3));
        gl.uniform1f(UQ('uF'), f * f * (3 - 2 * f) * (op.foto == null ? 1 : op.foto)); gl.uniform1f(UQ('uT'), t);
        gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, tex); gl.uniform1i(UQ('uTex'), 0);
        gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, foto); gl.uniform1i(UQ('uFoto'), 1);
        gl.activeTexture(gl.TEXTURE0);
        gl.bindVertexArray(qv); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      }
    };
    return api;
  };
  window.pinturaDuracao = 4.9 / VEL;
})();
