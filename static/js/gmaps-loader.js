/**
 * @fileoverview This file contains Google Maps JS SDK typings, which are
 * published as `@types/google.maps`. However, sometimes there is a delay
 * in published typings. Components should use types from this file so we
 * can centrally shim/unshim them when necessary.
 *
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
var t,e,i;!function(t){t.CONFIRMATION_LEVEL_UNSPECIFIED="CONFIRMATION_LEVEL_UNSPECIFIED",t.CONFIRMED="CONFIRMED",t.UNCONFIRMED_BUT_PLAUSIBLE="UNCONFIRMED_BUT_PLAUSIBLE",t.UNCONFIRMED_AND_SUSPICIOUS="UNCONFIRMED_AND_SUSPICIOUS"}(t||(t={})),function(t){t.GRANULARITY_UNSPECIFIED="GRANULARITY_UNSPECIFIED",t.SUB_PREMISE="SUB_PREMISE",t.PREMISE="PREMISE",t.PREMISE_PROXIMITY="PREMISE_PROXIMITY",t.BLOCK="BLOCK",t.ROUTE="ROUTE",t.OTHER="OTHER"}(e||(e={})),function(t){t.ACCEPT="ACCEPT",t.CONFIRM="CONFIRM",t.FIX="FIX",t.ADD_SUBPREMISES="ADD_SUBPREMISES"}(i||(i={}));const s="administrative_area_level_1",n="administrative_area_level_2",o="administrative_area_level_3",r="postal_code",a="postal_code_suffix",l="country",c="subpremise";function d(t){return function({verdict:t,address:e}){return!t||!e}(t)||function(t){const e=t.address?.missingComponentTypes||[];return e.length>1||1===e.length&&e[0]!==c}(t)||(d=t,!d.verdict?.validationGranularity||d.verdict.validationGranularity===e.OTHER)||function(t){return!!t.address?.components.some((t=>"UNCONFIRMED_AND_SUSPICIOUS"===t.confirmationLevel))}(t)||function(t){return!!t.address&&(t.address.unresolvedTokens||[]).length>0}(t)?{suggestedAction:i.FIX}:function(t){const e=new Set([r,a,s,n,o,l]);return!!t.address&&t.address.components.some((t=>t.isInferred&&!e.has(t.componentType)))}(t)||function(t){return!!t.verdict?.hasReplacedComponents}(t)?{suggestedAction:i.CONFIRM}:function(t){return!!t.address&&(e=t.address,"US"===e.postalAddress?.regionCode)&&1===t.address.missingComponentTypes?.length&&t.address.missingComponentTypes[0]===c;var e}(t)?{suggestedAction:i.ADD_SUBPREMISES}:{suggestedAction:i.ACCEPT};var d}function p(t,e,i,s){var n,o=arguments.length,r=o<3?e:null===s?s=Object.getOwnPropertyDescriptor(e,i):s;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)r=Reflect.decorate(t,e,i,s);else for(var a=t.length-1;a>=0;a--)(n=t[a])&&(r=(o<3?n(r):o>3?n(e,i,r):n(e,i))||r);return o>3&&r&&Object.defineProperty(e,i,r),r}function h(t,e){if("object"==typeof Reflect&&"function"==typeof Reflect.metadata)return Reflect.metadata(t,e)}"function"==typeof SuppressedError&&SuppressedError;
/**
 * @license
 * Copyright 2019 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const u=globalThis,g=u.ShadowRoot&&(void 0===u.ShadyCSS||u.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,m=Symbol(),f=new WeakMap;let y=class{constructor(t,e,i){if(this._$cssResult$=!0,i!==m)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(g&&void 0===t){const i=void 0!==e&&1===e.length;i&&(t=f.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),i&&f.set(e,t))}return t}toString(){return this.cssText}};const v=(t,...e)=>{const i=1===t.length?t[0]:e.reduce(((e,i,s)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+t[s+1]),t[0]);return new y(i,t,m)},b=g?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const i of t.cssRules)e+=i.cssText;return(t=>new y("string"==typeof t?t:t+"",void 0,m))(e)})(t):t
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */,{is:_,defineProperty:$,getOwnPropertyDescriptor:A,getOwnPropertyNames:x,getOwnPropertySymbols:E,getPrototypeOf:w}=Object,L=globalThis,O=L.trustedTypes,C=O?O.emptyScript:"",S=L.reactiveElementPolyfillSupport,P=(t,e)=>t,R={toAttribute(t,e){switch(e){case Boolean:t=t?C:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let i=t;switch(e){case Boolean:i=null!==t;break;case Number:i=null===t?null:Number(t);break;case Object:case Array:try{i=JSON.parse(t)}catch(t){i=null}}return i}},I=(t,e)=>!_(t,e),M={attribute:!0,type:String,converter:R,reflect:!1,hasChanged:I};Symbol.metadata??=Symbol("metadata"),L.litPropertyMetadata??=new WeakMap;class T extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=M){if(e.state&&(e.attribute=!1),this._$Ei(),this.elementProperties.set(t,e),!e.noAccessor){const i=Symbol(),s=this.getPropertyDescriptor(t,i,e);void 0!==s&&$(this.prototype,t,s)}}static getPropertyDescriptor(t,e,i){const{get:s,set:n}=A(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get(){return s?.call(this)},set(e){const o=s?.call(this);n.call(this,e),this.requestUpdate(t,o,i)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??M}static _$Ei(){if(this.hasOwnProperty(P("elementProperties")))return;const t=w(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(P("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(P("properties"))){const t=this.properties,e=[...x(t),...E(t)];for(const i of e)this.createProperty(i,t[i])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,i]of e)this.elementProperties.set(t,i)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const i=this._$Eu(t,e);void 0!==i&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const i=new Set(t.flat(1/0).reverse());for(const t of i)e.unshift(b(t))}else void 0!==t&&e.push(b(t));return e}static _$Eu(t,e){const i=e.attribute;return!1===i?void 0:"string"==typeof i?i:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise((t=>this.enableUpdating=t)),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach((t=>t(this)))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const i of e.keys())this.hasOwnProperty(i)&&(t.set(i,this[i]),delete this[i]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,e)=>{if(g)t.adoptedStyleSheets=e.map((t=>t instanceof CSSStyleSheet?t:t.styleSheet));else for(const i of e){const e=document.createElement("style"),s=u.litNonce;void 0!==s&&e.setAttribute("nonce",s),e.textContent=i.cssText,t.appendChild(e)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach((t=>t.hostConnected?.()))}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach((t=>t.hostDisconnected?.()))}attributeChangedCallback(t,e,i){this._$AK(t,i)}_$EC(t,e){const i=this.constructor.elementProperties.get(t),s=this.constructor._$Eu(t,i);if(void 0!==s&&!0===i.reflect){const n=(void 0!==i.converter?.toAttribute?i.converter:R).toAttribute(e,i.type);this._$Em=t,null==n?this.removeAttribute(s):this.setAttribute(s,n),this._$Em=null}}_$AK(t,e){const i=this.constructor,s=i._$Eh.get(t);if(void 0!==s&&this._$Em!==s){const t=i.getPropertyOptions(s),n="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:R;this._$Em=s,this[s]=n.fromAttribute(e,t.type),this._$Em=null}}requestUpdate(t,e,i){if(void 0!==t){if(i??=this.constructor.getPropertyOptions(t),!(i.hasChanged??I)(this[t],e))return;this.P(t,e,i)}!1===this.isUpdatePending&&(this._$ES=this._$ET())}P(t,e,i){this._$AL.has(t)||this._$AL.set(t,e),!0===i.reflect&&this._$Em!==t&&(this._$Ej??=new Set).add(t)}async _$ET(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,i]of t)!0!==i.wrapped||this._$AL.has(e)||void 0===this[e]||this.P(e,this[e],i)}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach((t=>t.hostUpdate?.())),this.update(e)):this._$EU()}catch(e){throw t=!1,this._$EU(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach((t=>t.hostUpdated?.())),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EU(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Ej&&=this._$Ej.forEach((t=>this._$EC(t,this[t]))),this._$EU()}updated(t){}firstUpdated(t){}}T.elementStyles=[],T.shadowRootOptions={mode:"open"},T[P("elementProperties")]=new Map,T[P("finalized")]=new Map,S?.({ReactiveElement:T}),(L.reactiveElementVersions??=[]).push("2.0.4");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const k=globalThis,N=k.trustedTypes,D=N?N.createPolicy("lit-html",{createHTML:t=>t}):void 0,U="$lit$",H=`lit$${(Math.random()+"").slice(9)}$`,B="?"+H,z=`<${B}>`,j=document,F=()=>j.createComment(""),W=t=>null===t||"object"!=typeof t&&"function"!=typeof t,q=Array.isArray,V=t=>q(t)||"function"==typeof t?.[Symbol.iterator],Y="[ \t\n\f\r]",G=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,K=/-->/g,X=/>/g,J=RegExp(`>|${Y}(?:([^\\s"'>=/]+)(${Y}*=${Y}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),Q=/'/g,Z=/"/g,tt=/^(?:script|style|textarea|title)$/i,et=(t=>(e,...i)=>({_$litType$:t,strings:e,values:i}))(1),it=Symbol.for("lit-noChange"),st=Symbol.for("lit-nothing"),nt=new WeakMap,ot=j.createTreeWalker(j,129);function rt(t,e){if(!Array.isArray(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==D?D.createHTML(e):e}const at=(t,e)=>{const i=t.length-1,s=[];let n,o=2===e?"<svg>":"",r=G;for(let e=0;e<i;e++){const i=t[e];let a,l,c=-1,d=0;for(;d<i.length&&(r.lastIndex=d,l=r.exec(i),null!==l);)d=r.lastIndex,r===G?"!--"===l[1]?r=K:void 0!==l[1]?r=X:void 0!==l[2]?(tt.test(l[2])&&(n=RegExp("</"+l[2],"g")),r=J):void 0!==l[3]&&(r=J):r===J?">"===l[0]?(r=n??G,c=-1):void 0===l[1]?c=-2:(c=r.lastIndex-l[2].length,a=l[1],r=void 0===l[3]?J:'"'===l[3]?Z:Q):r===Z||r===Q?r=J:r===K||r===X?r=G:(r=J,n=void 0);const p=r===J&&t[e+1].startsWith("/>")?" ":"";o+=r===G?i+z:c>=0?(s.push(a),i.slice(0,c)+U+i.slice(c)+H+p):i+H+(-2===c?e:p)}return[rt(t,o+(t[i]||"<?>")+(2===e?"</svg>":"")),s]};class lt{constructor({strings:t,_$litType$:e},i){let s;this.parts=[];let n=0,o=0;const r=t.length-1,a=this.parts,[l,c]=at(t,e);if(this.el=lt.createElement(l,i),ot.currentNode=this.el.content,2===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(s=ot.nextNode())&&a.length<r;){if(1===s.nodeType){if(s.hasAttributes())for(const t of s.getAttributeNames())if(t.endsWith(U)){const e=c[o++],i=s.getAttribute(t).split(H),r=/([.?@])?(.*)/.exec(e);a.push({type:1,index:n,name:r[2],strings:i,ctor:"."===r[1]?ut:"?"===r[1]?gt:"@"===r[1]?mt:ht}),s.removeAttribute(t)}else t.startsWith(H)&&(a.push({type:6,index:n}),s.removeAttribute(t));if(tt.test(s.tagName)){const t=s.textContent.split(H),e=t.length-1;if(e>0){s.textContent=N?N.emptyScript:"";for(let i=0;i<e;i++)s.append(t[i],F()),ot.nextNode(),a.push({type:2,index:++n});s.append(t[e],F())}}}else if(8===s.nodeType)if(s.data===B)a.push({type:2,index:n});else{let t=-1;for(;-1!==(t=s.data.indexOf(H,t+1));)a.push({type:7,index:n}),t+=H.length-1}n++}}static createElement(t,e){const i=j.createElement("template");return i.innerHTML=t,i}}function ct(t,e,i=t,s){if(e===it)return e;let n=void 0!==s?i._$Co?.[s]:i._$Cl;const o=W(e)?void 0:e._$litDirective$;return n?.constructor!==o&&(n?._$AO?.(!1),void 0===o?n=void 0:(n=new o(t),n._$AT(t,i,s)),void 0!==s?(i._$Co??=[])[s]=n:i._$Cl=n),void 0!==n&&(e=ct(t,n._$AS(t,e.values),n,s)),e}class dt{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:i}=this._$AD,s=(t?.creationScope??j).importNode(e,!0);ot.currentNode=s;let n=ot.nextNode(),o=0,r=0,a=i[0];for(;void 0!==a;){if(o===a.index){let e;2===a.type?e=new pt(n,n.nextSibling,this,t):1===a.type?e=new a.ctor(n,a.name,a.strings,this,t):6===a.type&&(e=new ft(n,this,t)),this._$AV.push(e),a=i[++r]}o!==a?.index&&(n=ot.nextNode(),o++)}return ot.currentNode=j,s}p(t){let e=0;for(const i of this._$AV)void 0!==i&&(void 0!==i.strings?(i._$AI(t,i,e),e+=i.strings.length-2):i._$AI(t[e])),e++}}class pt{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,i,s){this.type=2,this._$AH=st,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=i,this.options=s,this._$Cv=s?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=ct(this,t,e),W(t)?t===st||null==t||""===t?(this._$AH!==st&&this._$AR(),this._$AH=st):t!==this._$AH&&t!==it&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):V(t)?this.k(t):this._(t)}S(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.S(t))}_(t){this._$AH!==st&&W(this._$AH)?this._$AA.nextSibling.data=t:this.T(j.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:i}=t,s="number"==typeof i?this._$AC(t):(void 0===i.el&&(i.el=lt.createElement(rt(i.h,i.h[0]),this.options)),i);if(this._$AH?._$AD===s)this._$AH.p(e);else{const t=new dt(s,this),i=t.u(this.options);t.p(e),this.T(i),this._$AH=t}}_$AC(t){let e=nt.get(t.strings);return void 0===e&&nt.set(t.strings,e=new lt(t)),e}k(t){q(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let i,s=0;for(const n of t)s===e.length?e.push(i=new pt(this.S(F()),this.S(F()),this,this.options)):i=e[s],i._$AI(n),s++;s<e.length&&(this._$AR(i&&i._$AB.nextSibling,s),e.length=s)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t&&t!==this._$AB;){const e=t.nextSibling;t.remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class ht{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,i,s,n){this.type=1,this._$AH=st,this._$AN=void 0,this.element=t,this.name=e,this._$AM=s,this.options=n,i.length>2||""!==i[0]||""!==i[1]?(this._$AH=Array(i.length-1).fill(new String),this.strings=i):this._$AH=st}_$AI(t,e=this,i,s){const n=this.strings;let o=!1;if(void 0===n)t=ct(this,t,e,0),o=!W(t)||t!==this._$AH&&t!==it,o&&(this._$AH=t);else{const s=t;let r,a;for(t=n[0],r=0;r<n.length-1;r++)a=ct(this,s[i+r],e,r),a===it&&(a=this._$AH[r]),o||=!W(a)||a!==this._$AH[r],a===st?t=st:t!==st&&(t+=(a??"")+n[r+1]),this._$AH[r]=a}o&&!s&&this.j(t)}j(t){t===st?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class ut extends ht{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===st?void 0:t}}class gt extends ht{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==st)}}class mt extends ht{constructor(t,e,i,s,n){super(t,e,i,s,n),this.type=5}_$AI(t,e=this){if((t=ct(this,t,e,0)??st)===it)return;const i=this._$AH,s=t===st&&i!==st||t.capture!==i.capture||t.once!==i.once||t.passive!==i.passive,n=t!==st&&(i===st||s);s&&this.element.removeEventListener(this.name,this,i),n&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class ft{constructor(t,e,i){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=i}get _$AU(){return this._$AM._$AU}_$AI(t){ct(this,t)}}const yt={P:U,A:H,C:B,M:1,L:at,R:dt,D:V,V:ct,I:pt,H:ht,N:gt,U:mt,B:ut,F:ft},vt=k.litHtmlPolyfillSupport;vt?.(lt,pt),(k.litHtmlVersions??=[]).push("3.1.2");const bt=(t,e,i)=>{const s=i?.renderBefore??e;let n=s._$litPart$;if(void 0===n){const t=i?.renderBefore??null;s._$litPart$=n=new pt(e.insertBefore(F(),t),t,void 0,i??{})}return n._$AI(t),n
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */};let _t=class extends T{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=bt(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return it}};_t._$litElement$=!0,_t.finalized=!0,globalThis.litElementHydrateSupport?.({LitElement:_t});const $t=globalThis.litElementPolyfillSupport;$t?.({LitElement:_t}),(globalThis.litElementVersions??=[]).push("4.0.4");
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const At=t=>(e,i)=>{void 0!==i?i.addInitializer((()=>{customElements.define(t,e)})):customElements.define(t,e)}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */,xt={attribute:!0,type:String,converter:R,reflect:!1,hasChanged:I},Et=(t=xt,e,i)=>{const{kind:s,metadata:n}=i;let o=globalThis.litPropertyMetadata.get(n);if(void 0===o&&globalThis.litPropertyMetadata.set(n,o=new Map),o.set(i.name,t),"accessor"===s){const{name:s}=i;return{set(i){const n=e.get.call(this);e.set.call(this,i),this.requestUpdate(s,n,t)},init(e){return void 0!==e&&this.P(s,void 0,t),e}}}if("setter"===s){const{name:s}=i;return function(i){const n=this[s];e.call(this,i),this.requestUpdate(s,n,t)}}throw Error("Unsupported decorator location: "+s)};function wt(t){return(e,i)=>"object"==typeof i?Et(t,e,i):((t,e,i)=>{const s=e.hasOwnProperty(i);return e.constructor.createProperty(i,s?{...t,wrapped:!0}:t),s?Object.getOwnPropertyDescriptor(e,i):void 0})(t,e,i)
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */}function Lt(t){return wt({...t,state:!0,attribute:!1})}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */const Ot=(t,e,i)=>(i.configurable=!0,i.enumerable=!0,Reflect.decorate&&"object"!=typeof e&&Object.defineProperty(t,e,i),i)
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */;function Ct(t,e){return(i,s,n)=>{const o=e=>e.renderRoot?.querySelector(t)??null;if(e){const{get:t,set:e}="object"==typeof s?i:n??(()=>{const t=Symbol();return{get(){return this[t]},set(e){this[t]=e}}})();return Ot(i,s,{get(){let i=t.call(this);return void 0===i&&(i=o(this),(null!==i||this.hasUpdated)&&e.call(this,i)),i}})}return Ot(i,s,{get(){return o(this)}})}}
/**
 * @license
 * Copyright 2021 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function St(t){return(e,i)=>{const{slot:s,selector:n}=t??{},o="slot"+(s?`[name=${s}]`:":not([name])");return Ot(e,i,{get(){const e=this.renderRoot?.querySelector(o),i=e?.assignedElements(t)??[];return void 0===n?i:i.filter((t=>t.matches(n)))}})}}
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
class Pt{constructor(t){this.host=t,this.host.addController(this)}hostUpdate(){}info(t,...e){console.info(this.formatMessage(t),...e)}warn(t,...e){console.warn(this.formatMessage(t),...e)}error(t,...e){console.error(this.formatMessage(t),...e)}formatMessage(t){return this.prependTagName(t)}prependTagName(t){return`<${this.host.tagName.toLowerCase()}>: ${t}`}}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */class Rt extends _t{constructor(){super(...arguments),this.logger=new Pt(this)}}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
class It{constructor(){this.promise=new Promise(((t,e)=>{this.resolveCallback=t,this.rejectCallback=e}))}resolve(t){this.value=t,this.resolveCallback(t)}reject(t){this.rejectCallback(t)}}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */var Mt,Tt={load:function(t){return(t=>{var e,i,s,n="The Google Maps JavaScript API",o="google",r="importLibrary",a="__ib__",l=document,c=window,d=(c=c[o]||(c[o]={})).maps||(c.maps={}),p=new Set,h=new URLSearchParams;d[r]?console.warn(n+" only loads once. Ignoring:",t):d[r]=(c,...u)=>p.add(c)&&(e||(e=new Promise((async(r,c)=>{for(s in await(i=l.createElement("script")),h.set("libraries",[...p]+""),t)h.set(s.replace(/[A-Z]/g,(t=>"_"+t[0].toLowerCase())),t[s]);h.set("callback",o+".maps."+a),i.src=`https://maps.${o}apis.com/maps/api/js?`+h,d[a]=r,i.onerror=()=>e=c(Error(n+" could not load.")),i.nonce=l.querySelector("script[nonce]")?.nonce||"",l.head.append(i)})))).then((()=>d[r](c,...u)))})(t),google.maps}};
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */function kt(t){t.importLibrary("maps"),t.importLibrary("marker")}let Nt=Mt=class extends Rt{constructor(){super(...arguments),this.version="beta"}set apiKey(t){this.key=t}get apiKey(){return this.key}async connectedCallback(){super.connectedCallback(),Mt.instance?this.logger.warn("Found multiple instances of this element on the same page. The Google Maps JavaScript API can only be configured once; please ensure you only have a single instance.",this):Mt.instance=this}willUpdate(t){Mt.instance===this&&this.tryLoadGoogleMapsAPI(t)}render(){return et`<slot></slot>`}getSolutionChannel(){if(""!==this.solutionChannel)return this.solutionChannel?this.solutionChannel:"GMP_CDN_extended_v0.6.14"}tryLoadGoogleMapsAPI(t){if(Mt.googleMapsDeferred.value)if(Mt.inlineScriptLoaded){const e=t.keys().next().value;this.logger.warn(`Property '${e}' cannot be updated once the Google Maps JavaScript API is already loaded.`)}else this.logger.warn("Please remove the <gmpx-api-loader> element if you are using the Google Maps JavaScript API inline bootstrap loader. Duplicate configuration may cause unexpected behavior.");else if(void 0!==this.key){const{key:t,version:e,language:i,region:s,authReferrerPolicy:n}=this,o=this.getSolutionChannel(),r=Tt.load({key:t,...e&&{v:e},...i&&{language:i},...s&&{region:s},...o&&{solutionChannel:o},...n&&{authReferrerPolicy:n}});Mt.inlineScriptLoaded=!0,Mt.googleMapsDeferred.resolve(r),kt(r)}}static async importLibrary(t,e){let i=Mt.googleMapsDeferred.value;return i||(Mt.pollForGoogleMaps(5,1e3,e&&function(t){const e=t.logger;return e instanceof Pt?e:void 0}(e)),i=await Mt.googleMapsDeferred.promise),i.importLibrary(t)}static reset(){delete window.google,delete Mt.instance,Mt.inlineScriptLoaded=!1,Mt.googleMapsDeferred=new It}static pollForGoogleMaps(t,e,i,s=0){const n=function(){try{return google?.maps}catch(t){return}}();if(n)!Mt.inlineScriptLoaded&&s>0&&(i??console).warn("Using the legacy Google Maps JavaScript API script loader may result in suboptimal performance. For best results, please include a <gmpx-api-loader> (https://github.com/googlemaps/extended-component-library) or use the inline bootstrap loader (https://goo.gle/js-api-loading) instead."),Mt.googleMapsDeferred.resolve(n),kt(n);else{if(!(t>0)){let t=i?i.formatMessage("The Google Maps JavaScript API is required for this element to function correctly. "):"APILoader.importLibrary(): Unable to initialize the Google Maps JavaScript API. ";throw t+="Please ensure you have a <gmpx-api-loader> on the page with a valid API key. https://github.com/googlemaps/extended-component-library",new Error(t)}window.setTimeout((()=>{Mt.pollForGoogleMaps(t-1,e,i,s+1)}),e)}}};Nt.googleMapsDeferred=new It,Nt.inlineScriptLoaded=!1,p([wt({attribute:"auth-referrer-policy",reflect:!0,type:String}),h("design:type",String)],Nt.prototype,"authReferrerPolicy",void 0),p([wt({reflect:!0,type:String}),h("design:type",String)],Nt.prototype,"key",void 0),p([wt({reflect:!0,type:String}),h("design:type",String)],Nt.prototype,"language",void 0),p([wt({reflect:!0,type:String}),h("design:type",String)],Nt.prototype,"region",void 0),p([wt({attribute:"solution-channel",reflect:!0,type:String}),h("design:type",String)],Nt.prototype,"solutionChannel",void 0),p([wt({reflect:!0,type:String}),h("design:type",Object)],Nt.prototype,"version",void 0),Nt=Mt=p([At("gmpx-api-loader")],Nt);
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const Dt=1,Ut=2,Ht=t=>(...e)=>({_$litDirective$:t,values:e});let Bt=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,e,i){this._$Ct=t,this._$AM=e,this._$Ci=i}_$AS(t,e){return this.update(t,e)}update(t,e){return this.render(...e)}};
/**
 * @license
 * Copyright 2018 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */const zt=Ht(class extends Bt{constructor(t){if(super(t),t.type!==Dt||"class"!==t.name||t.strings?.length>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(t){return" "+Object.keys(t).filter((e=>t[e])).join(" ")+" "}update(t,[e]){if(void 0===this.st){this.st=new Set,void 0!==t.strings&&(this.nt=new Set(t.strings.join(" ").split(/\s/).filter((t=>""!==t))));for(const t in e)e[t]&&!this.nt?.has(t)&&this.st.add(t);return this.render(e)}const i=t.element.classList;for(const t of this.st)t in e||(i.remove(t),this.st.delete(t));for(const t in e){const s=!!e[t];s===this.st.has(t)||this.nt?.has(t)||(s?(i.add(t),this.st.add(t)):(i.remove(t),this.st.delete(t)))}return it}});
/**
 * @license
 * Copyright 2021 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function jt(t,e,i){return t?e(t):i?.(t)}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */const Ft=v`var(--gmpx-color-primary, #1976d2)`,Wt=v`var(--gmpx-color-surface, #fff)`,qt=v`var(--gmpx-color-on-primary, #fff)`,Vt=v`var(--gmpx-color-on-surface, #212121)`,Yt=v`var(--gmpx-color-on-surface-variant, #757575)`,Gt=v`var(--gmpx-color-outline, #e0e0e0)`,Kt=v`var(--gmpx-rating-color, #ffb300)`,Xt=v`var(--gmpx-rating-color-empty, #e0e0e0)`,Jt=v`var(--gmpx-font-family-base, 'Google Sans Text', sans-serif)`,Qt=v`var(--gmpx-font-family-headings, ${Jt})`,Zt=v`var(--gmpx-font-size-base, 0.875rem)`;function te(t){return v`calc(${Zt} * (${t}/14))`}const ee=v`400 ${te(18)}/${te(24)} ${Qt}`,ie=v`500 ${te(16)}/${te(24)} ${Qt}`,se=v`500 ${te(14)}/${te(20)} ${Qt}`,ne=v`400 ${te(14)}/${te(20)} ${Jt}`,oe=v`400 ${te(12)}/${te(16)} ${Jt}`,re=v`1px solid ${Gt}`
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */;function ae(t){const e=document.createElement("div");e.innerHTML=t;const i=e.querySelector("a");return{text:e.textContent||void 0,url:i&&i.href||void 0}}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */var le;!function(t){t.GOOGLE_SANS_TEXT="Google Sans Text",t.MATERIAL_SYMBOLS_OUTLINED="Material Symbols Outlined"}(le||(le={}));const ce=Object.freeze({[le.GOOGLE_SANS_TEXT]:{loadInDocumentHead:!0,loadInShadowRoot:!1,weights:[400,500]},[le.MATERIAL_SYMBOLS_OUTLINED]:{loadInDocumentHead:!0,loadInShadowRoot:!0,weights:[400]}});class de{constructor(t,e){this.host=t,this.fonts=e,t.addController(this);for(const t of e)ce[t].loadInDocumentHead&&this.injectWebFontAsset(document.head,t)}hostConnected(){for(const t of this.fonts)ce[t].loadInShadowRoot&&this.injectWebFontAsset(this.host.renderRoot,t)}injectWebFontAsset(t,e){t.querySelector(`link[href*="${encodeURIComponent(e)}"]`)||t.appendChild(function(t,e){const i=document.createElement("link");return i.rel="stylesheet",i.href=`https://fonts.googleapis.com/css2?family=${encodeURIComponent(t)}:wght@${encodeURIComponent(e.join(";"))}`,i}(e,ce[e].weights))}}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */const pe=Object.freeze(["outlined","filled"]),he=.5;let ue=class extends Rt{constructor(){super(...arguments),this.ariaHasPopup="false",this.ariaLabel=null,this.condensed=!1,this.variant="outlined",this.hasLabel=!1,this.fontLoader=new de(this,[le.GOOGLE_SANS_TEXT,le.MATERIAL_SYMBOLS_OUTLINED])}willUpdate(t){t.has("variant")&&!pe.includes(this.variant)&&(this.logger.error(`Value "${this.variant}" for attribute "variant" is invalid. Acceptable choices are ${pe.map((t=>`"${t}"`)).join(", ")}.`),this.variant="outlined")}render(){return this.href?et`
        <a
          aria-label=${this.ariaLabel??st}
          class="container"
          href=${this.href}
          target="_blank"
        >${this.renderContent()}</a>
      `:et`
      <button
        aria-haspopup=${this.ariaHasPopup}
        aria-label=${this.ariaLabel??st}
        class="container"
      >${this.renderContent()}</button>
    `}updated(){this.role=null!=this.ariaLabel?"none":null}renderContent(){const t=this.icon||(!this.hasLabel||this.condensed?"add":void 0);return et`
      <div class="layout ${zt({condensed:this.condensed,"no-label":!this.hasLabel})}">
        <div class="pill ${zt({filled:"filled"===this.variant,outlined:"filled"!==this.variant})}">
          <div class="overlay"></div>
          ${jt(t,(()=>et`
            <span aria-hidden="true" class="icon material-symbols-outlined">
              ${t}
            </span>
          `))}
          ${jt(!this.condensed,(()=>this.renderLabel()))}
        </div>
        ${jt(this.condensed,(()=>this.renderLabel()))}
      </div>
    `}renderLabel(){return et`
      <div class="label-container">
        <slot @slotchange=${this.handleSlotChange}></slot>
      </div>
    `}handleSlotChange(){this.hasLabel=Boolean(this.defaultSlotNodes?.map((t=>t.textContent??"")).join("").trim())}};ue.styles=v`
    .container {
      all: unset;
      color: ${Ft};
      cursor: pointer;
      text-align: center;
    }

    .icon {
      font-size: ${te(18)};
    }

    .layout.condensed {
      display: flex;
      flex-direction: column;
    }

    .layout.condensed .pill {
      align-self: center;
    }

    .layout.condensed .label-container {
      font: ${oe};
      margin-top: calc(${Zt} * ${he});
    }

    .layout.no-label .label-container {
      margin: 0;
    }

    .layout:not(.condensed):not(.no-label) .pill {
      padding-left: calc(${Zt} * ${he});
      padding-right: calc(${Zt} * ${he});
    }

    .pill {
      align-items: center;
      border-radius: calc(${Zt} * (1 + ${he}));
      display: flex;
      font: ${se};
      justify-content: center;
      overflow: hidden;
      padding: calc(${Zt} * ${he} / 2);
      position: relative;
    }

    .pill > * {
      margin: calc(${Zt} * ${he} / 2);
    }

    .pill.filled {
      background-color: ${Ft};
      color: ${qt};
    }

    .pill.outlined {
      border: ${re};
    }

    .pill .overlay {
      inset: 0;
      margin: 0;
      opacity: 0;
      position: absolute;
    }

    .pill.outlined .overlay {
      background-color: ${Ft};
    }

    .pill.filled .overlay {
      background-color: ${qt};
    }

    .container:hover .overlay {
      opacity: 0.08;
    }

    .container:focus .overlay {
      opacity: 0.24;
    }

    .container:active .overlay {
      opacity: 0.32;
    }
  `,ue.shadowRootOptions={...Rt.shadowRootOptions,delegatesFocus:!0},p([wt({attribute:"aria-haspopup",reflect:!0,type:String}),h("design:type",String)],ue.prototype,"ariaHasPopup",void 0),p([wt({attribute:"aria-label",reflect:!0,type:String}),h("design:type",Object)],ue.prototype,"ariaLabel",void 0),p([wt({reflect:!0,type:Boolean}),h("design:type",Object)],ue.prototype,"condensed",void 0),p([wt({reflect:!0,type:String}),h("design:type",String)],ue.prototype,"href",void 0),p([wt({reflect:!0,type:String}),h("design:type",String)],ue.prototype,"icon",void 0),p([wt({reflect:!0,type:String}),h("design:type",String)],ue.prototype,"variant",void 0),p([Lt(),h("design:type",Object)],ue.prototype,"hasLabel",void 0),p([function(t){return(e,i)=>{const{slot:s}=t??{},n="slot"+(s?`[name=${s}]`:":not([name])");return Ot(e,i,{get(){const e=this.renderRoot?.querySelector(n);return e?.assignedNodes(t)??[]}})}}({flatten:!0}),h("design:type",Array)],ue.prototype,"defaultSlotNodes",void 0),ue=p([At("gmpx-icon-button")],ue);
/**
 * @license
 * Copyright 2018 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const ge="important",me=" !"+ge,fe=Ht(class extends Bt{constructor(t){if(super(t),t.type!==Dt||"style"!==t.name||t.strings?.length>2)throw Error("The `styleMap` directive must be used in the `style` attribute and must be the only part in the attribute.")}render(t){return Object.keys(t).reduce(((e,i)=>{const s=t[i];return null==s?e:e+`${i=i.includes("-")?i:i.replace(/(?:^(webkit|moz|ms|o)|)(?=[A-Z])/g,"-$&").toLowerCase()}:${s};`}),"")}update(t,[e]){const{style:i}=t.element;if(void 0===this.ft)return this.ft=new Set(Object.keys(e)),this.render(e);for(const t of this.ft)null==e[t]&&(this.ft.delete(t),t.includes("-")?i.removeProperty(t):i[t]=null);for(const t in e){const s=e[t];if(null!=s){this.ft.add(t);const e="string"==typeof s&&s.endsWith(me);t.includes("-")||e?i.setProperty(t,e?s.slice(0,-11):s,e?ge:""):i[t]=s}}return it}});
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */function ye(t){return t?`"${t}"`:"default"}class ve{constructor(t,e,i){this.host=t,this.logger=e,this.supportedSlotNames=i,t.addController(this)}hostConnected(){for(const t of this.host.children)this.checkChildSlotValidity(t)}checkChildSlotValidity(t){const e=t.getAttribute("slot")??"";this.supportedSlotNames.includes(e)||this.logger.warn(`Detected child element in unsupported ${ye(e)} slot. This component supports the following slots: ${this.supportedSlotNames.map(ye).join(", ")}.`,t)}}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */function be(){let t,e=document.activeElement;if(!e)return null;for(;t=e.shadowRoot?.activeElement;)e=t;return e}function*_e(t){for(;;)if(yield t,t.parentNode)t=t.parentNode;else{if(!(t instanceof ShadowRoot))return;t=t.host}}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
let $e=class extends Rt{constructor(){super(...arguments),this.opened=!1,this.mainLastActiveEl=null,this.slotValidator=new ve(this,this.logger,["main","overlay"])}async showOverlay(){if(!this.opened&&(this.mainLastActiveEl=this.getMainActiveEl(),this.opened=!0,await this.updateComplete,this.overlayContainer.scroll(0,0),this.mainLastActiveEl)){const t=this.getOverlayAutofocusEl();t?t.focus():this.overlayContainer.focus()}}async hideOverlay(){if(!this.opened)return;const t=this.getOverlayActiveEl();this.opened=!1,(t||be()===this.overlayContainer)&&(await this.updateComplete,this.mainLastActiveEl?this.mainLastActiveEl.focus():this.mainContainer.focus()),this.mainLastActiveEl=null}render(){return et`
      <div class="outer-container">
        <div
          class="inner-container main-container"
          style=${fe({display:this.opened?"none":"block"})}
          tabindex="-1"
        >
          <slot name="main"></slot>
        </div>
        <div
          class="inner-container overlay-container"
          style=${fe({display:this.opened?"block":"none"})}
          tabindex="-1"
          @keydown=${this.handleOverlayKeydown}
        >
          <slot name="overlay"></slot>
        </div>
      </div>
    `}handleOverlayKeydown(t){"Escape"===t.key&&this.hideOverlay()}getContainedActiveEl(t){const e=be();return e instanceof HTMLElement&&function(t,e){if(0===t.length||!e)return!1;const i=new Set(t);for(const t of _e(e))if(i.has(t))return!0;return!1}(t,e)?e:null}getMainActiveEl(){return this.getContainedActiveEl(this.mainAssignedEls)}getOverlayActiveEl(){return this.getContainedActiveEl(this.overlayAssignedEls)}getOverlayAutofocusEl(){for(const t of this.overlayAssignedEls){const e=t.querySelector("[autofocus]");if(e&&e instanceof HTMLElement)return e}return null}};
/**
 * @license
 * Copyright 2021 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
function*Ae(t,e){const i="function"==typeof e;if(void 0!==t){let s=-1;for(const n of t)s>-1&&(yield i?e(s):e),s++,yield n}}
/**
 * @license
 * Copyright 2021 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function*xe(t,e){if(void 0!==t){let i=0;for(const s of t)yield e(s,i++)}}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */$e.styles=v`
    :host(:not([hidden])) {
      display: block;
      height: 100%;
    }
    .outer-container {
      display: block;
      height: 100%;
      position: relative;
    }
    .inner-container {
      inset: 0;
      overflow: auto;
      position: absolute;
    }
    .inner-container:focus-visible {
      outline: none;
    }
  `,p([St({slot:"main"}),h("design:type",Array)],$e.prototype,"mainAssignedEls",void 0),p([St({slot:"overlay"}),h("design:type",Array)],$e.prototype,"overlayAssignedEls",void 0),p([Ct(".main-container"),h("design:type",HTMLDivElement)],$e.prototype,"mainContainer",void 0),p([Ct(".overlay-container"),h("design:type",HTMLDivElement)],$e.prototype,"overlayContainer",void 0),p([Lt(),h("design:type",Object)],$e.prototype,"opened",void 0),$e=p([At("gmpx-overlay-layout")],$e);const Ee=864e5,we=7*Ee;function Le(t,e,i=new Date){return function(t,e=!1){const i=new Date;return i.setDate(i.getDate()-i.getDay()+t.day),i.setHours(t.hour),i.setMinutes(t.minute),i.setSeconds(0),i.toLocaleString(void 0,{hour:"numeric",minute:"numeric",weekday:e?"short":void 0})}(t,!Oe(e,i))}function Oe(t,e=new Date,i=Ee){return t>=e&&t.valueOf()-e.valueOf()<i}function Ce(t){return 1===t.periods?.length&&!t.periods[0].close&&0===t.periods[0].open.day&&0===t.periods[0].open.hour&&0===t.periods[0].open.minute}function Se(t,e){const{year:i,month:s,day:n}=function(t){const e=new Date(t);return e.setUTCDate(e.getUTCDate()-e.getUTCDay()),{year:e.getUTCFullYear(),month:e.getUTCMonth(),day:e.getUTCDate()}}(t);let o=Date.UTC(i,s,n,0,-e);const r=t.valueOf()-o;return r<0?o-=we:r>=we&&(o+=we),new Date(o)}function Pe(t,e){const i=new Date(e);return i.setDate(i.getDate()+t.day),i.setHours(i.getHours()+t.hour),i.setMinutes(i.getMinutes()+t.minute),i}function Re(t,e,i=new Date){const s=Se(i,e);for(const e of t.periods){const t={period:e,openDate:Pe(e.open,s),closeDate:e.close?Pe(e.close,s):void 0};if(!t.closeDate)return t;if(t.closeDate<t.openDate&&(t.openDate>i?t.openDate.setDate(t.openDate.getDate()-7):t.closeDate.setDate(t.closeDate.getDate()+7)),i>=t.openDate&&i<t.closeDate)return t}return{}}var Ie,Me;
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
function Te(t){return!t.hasOwnProperty("id")}function ke(t){return function(t){return t.hasOwnProperty("id")}(t)?{location:t.location?.toJSON()??void 0,placeId:t.id,query:t.formattedAddress??t.displayName??void 0}:function(t){return"function"==typeof t.lat}(t)?{location:t.toJSON()}:{location:t}}!function(t){t[t.UNKNOWN=0]="UNKNOWN",t[t.ALWAYS_OPEN=1]="ALWAYS_OPEN",t[t.NOT_OPEN_NOW=2]="NOT_OPEN_NOW",t[t.WILL_CLOSE=3]="WILL_CLOSE"}(Ie||(Ie={})),function(t){t[t.UNKNOWN=0]="UNKNOWN",t[t.NEVER_OPEN=1]="NEVER_OPEN",t[t.ALREADY_OPEN=2]="ALREADY_OPEN",t[t.WILL_OPEN=3]="WILL_OPEN"}(Me||(Me={}));const Ne=Object.freeze({FREE:0,INEXPENSIVE:1,MODERATE:2,EXPENSIVE:3,VERY_EXPENSIVE:4}),De=Object.freeze(Object.fromEntries(Object.entries(Ne).map((t=>t.reverse()))));function Ue(t,e){return e?et`<a href=${e} target="_blank">${t}</a>`:et`<span>${t}</span>`}async function He(t,e){const i=await Nt.importLibrary("places",e),s=new i.Place({id:t.place_id??"PLACE_ID_MISSING"});let n=ze(t);return new Proxy(s,{get(t,e,o){if("fetchFields"===e)return async e=>{const o=e.fields.filter((t=>void 0===n[t]));try{return await t.fetchFields({...e,fields:o})}catch(t){if(qe(t,"fetchFields()")){const t=We(o);if(!t.length)return{place:s};const e=await async function(t,e,i){const s=new t.PlacesService(document.createElement("div"));return new Promise(((t,n)=>{s.getDetails({placeId:e,fields:i},((e,i)=>{e&&"OK"===i?t(e):n(i)}))}))}
/**
 * @license
 * Copyright 2021 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */(i,s.id,t);return n={...ze(e),...n},{place:s}}throw t}};if("isOpen"===e)return async i=>{try{return await Reflect.get(t,e,o).apply(o,[i])}catch(t){if(qe(t,"isOpen()"))return function(t,e=new Date){if(!t.regularOpeningHours||null==t.utcOffsetMinutes)return;if(Ce(t.regularOpeningHours))return!0;const{period:i}=Re(t.regularOpeningHours,t.utcOffsetMinutes,e);return!!i}(o,i);throw t}};const r=n[e];return void 0===r?Reflect.get(t,e,o):r}})}function Be(t){return!(!t.businessStatus||!t.regularOpeningHours||null==t.utcOffsetMinutes)}function ze(t){const e={};if(void 0!==t.address_components&&(e.addressComponents=t.address_components.map((t=>({longText:t.long_name,shortText:t.short_name,types:t.types})))),void 0!==t.adr_address&&(e.adrFormatAddress=t.adr_address),void 0!==t.business_status&&(e.businessStatus=t.business_status),void 0!==t.formatted_address&&(e.formattedAddress=t.formatted_address),void 0!==t.formatted_phone_number&&(e.nationalPhoneNumber=t.formatted_phone_number),void 0!==t.geometry){const i=t.geometry;i.location&&(e.location=i.location),i.viewport&&(e.viewport=i.viewport)}if(void 0!==t.html_attributions&&(e.attributions=t.html_attributions.map((t=>{const{text:e,url:i}=ae(t);return{provider:e??"",providerURI:i??null}}))),void 0!==t.icon_background_color&&(e.iconBackgroundColor=t.icon_background_color),void 0!==t.icon_mask_base_uri&&(e.svgIconMaskURI=t.icon_mask_base_uri),void 0!==t.international_phone_number&&(e.internationalPhoneNumber=t.international_phone_number),void 0!==t.name&&(e.displayName=t.name),void 0!==t.opening_hours){const i=t.opening_hours.periods?.map((t=>({open:je(t.open),close:t.close?je(t.close):null})));e.regularOpeningHours={periods:i??[],weekdayDescriptions:t.opening_hours.weekday_text??[]}}var i;return void 0!==t.photos&&(e.photos=t.photos.map((t=>({authorAttributions:t.html_attributions.map((t=>{const{text:e,url:i}=ae(t);return{displayName:e??"",photoURI:"",uri:i||""}})),getURI:t.getUrl,heightPx:t.height,widthPx:t.width})))),void 0!==t.place_id&&(e.id=t.place_id),void 0!==t.plus_code&&(e.plusCode={compoundCode:t.plus_code.compound_code??null,globalCode:t.plus_code.global_code}),void 0!==t.price_level&&(e.priceLevel="number"!=typeof(i=t.price_level)?i:De[i]??null),void 0!==t.rating&&(e.rating=t.rating),void 0!==t.reviews&&(e.reviews=t.reviews.map((t=>({authorAttribution:{displayName:t.author_name,photoURI:t.profile_photo_url,uri:t.author_url||""},publishTime:new Date(t.time),rating:t.rating??null,relativePublishTimeDescription:t.relative_time_description,text:t.text,textLanguageCode:t.language})))),void 0!==t.types&&(e.types=t.types),void 0!==t.url&&(e.googleMapsURI=t.url),void 0!==t.user_ratings_total&&(e.userRatingCount=t.user_ratings_total),void 0!==t.utc_offset_minutes&&(e.utcOffsetMinutes=t.utc_offset_minutes),void 0!==t.website&&(e.websiteURI=t.website),e}function je({day:t,hours:e,minutes:i}){return{day:t,hour:e,minute:i}}const Fe={addressComponents:"address_components",adrFormatAddress:"adr_address",businessStatus:"business_status",formattedAddress:"formatted_address",nationalPhoneNumber:"formatted_phone_number",location:"geometry",viewport:"geometry",iconBackgroundColor:"icon_background_color",svgIconMaskURI:"icon_mask_base_uri",internationalPhoneNumber:"international_phone_number",displayName:"name",regularOpeningHours:"opening_hours",photos:"photos",plusCode:"plus_code",priceLevel:"price_level",rating:"rating",reviews:"reviews",types:"types",googleMapsURI:"url",userRatingCount:"user_ratings_total",utcOffsetMinutes:"utc_offset_minutes",websiteURI:"website",id:"place_id"};function We(t){const e=[];for(const i of t){const t=Fe[i];t&&e.push(t)}return e}function qe(t,e){return t instanceof Error&&(t.message.startsWith(`Place.prototype.${e} is not available`)||t.message.startsWith(`google.maps.places.Place.${e} is not available`))}let Ve=class extends Event{constructor(t,e,i){super("context-request",{bubbles:!0,composed:!0}),this.context=t,this.callback=e,this.subscribe=i??!1}};
/**
 * @license
 * Copyright 2021 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
/**
 * @license
 * Copyright 2021 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
let Ye=class{constructor(t,e,i,s){if(this.subscribe=!1,this.provided=!1,this.value=void 0,this.t=(t,e)=>{this.unsubscribe&&(this.unsubscribe!==e&&(this.provided=!1,this.unsubscribe()),this.subscribe||this.unsubscribe()),this.value=t,this.host.requestUpdate(),this.provided&&!this.subscribe||(this.provided=!0,this.callback&&this.callback(t,e)),this.unsubscribe=e},this.host=t,void 0!==e.context){const t=e;this.context=t.context,this.callback=t.callback,this.subscribe=t.subscribe??!1}else this.context=e,this.callback=i,this.subscribe=s??!1;this.host.addController(this)}hostConnected(){this.dispatchRequest()}hostDisconnected(){this.unsubscribe&&(this.unsubscribe(),this.unsubscribe=void 0)}dispatchRequest(){this.host.dispatchEvent(new Ve(this.context,this.t,this.subscribe))}},Ge=class{get value(){return this.o}set value(t){this.setValue(t)}setValue(t,e=!1){const i=e||!Object.is(t,this.o);this.o=t,i&&this.updateObservers()}constructor(t){this.subscriptions=new Map,this.updateObservers=()=>{for(const[t,{disposer:e}]of this.subscriptions)t(this.o,e)},void 0!==t&&(this.value=t)}addCallback(t,e,i){if(!i)return void t(this.value);this.subscriptions.has(t)||this.subscriptions.set(t,{disposer:()=>{this.subscriptions.delete(t)},consumerHost:e});const{disposer:s}=this.subscriptions.get(t);t(this.value,s)}clearCallbacks(){this.subscriptions.clear()}},Ke=class extends Event{constructor(t){super("context-provider",{bubbles:!0,composed:!0}),this.context=t}};
/**
 * @license
 * Copyright 2021 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */class Xe extends Ge{constructor(t,e,i){super(void 0!==e.context?e.initialValue:i),this.onContextRequest=t=>{const e=t.composedPath()[0];t.context===this.context&&e!==this.host&&(t.stopPropagation(),this.addCallback(t.callback,e,t.subscribe))},this.onProviderRequest=t=>{const e=t.composedPath()[0];if(t.context!==this.context||e===this.host)return;const i=new Set;for(const[t,{consumerHost:e}]of this.subscriptions)i.has(t)||(i.add(t),e.dispatchEvent(new Ve(this.context,t,!0)));t.stopPropagation()},this.host=t,void 0!==e.context?this.context=e.context:this.context=e,this.attachListeners(),this.host.addController?.(this)}attachListeners(){this.host.addEventListener("context-request",this.onContextRequest),this.host.addEventListener("context-provider",this.onProviderRequest)}hostConnected(){this.host.dispatchEvent(new Ke(this.context))}}
/**
 * @license
 * Copyright 2021 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */let Je=class{constructor(){this.pendingContextRequests=new Map,this.onContextProvider=t=>{const e=this.pendingContextRequests.get(t.context);if(void 0===e)return;this.pendingContextRequests.delete(t.context);const{requests:i}=e;for(const{elementRef:e,callbackRef:s}of i){const i=e.deref(),n=s.deref();void 0===i||void 0===n||i.dispatchEvent(new Ve(t.context,n,!0))}},this.onContextRequest=t=>{if(!0!==t.subscribe)return;const e=t.composedPath()[0],i=t.callback;let s=this.pendingContextRequests.get(t.context);void 0===s&&this.pendingContextRequests.set(t.context,s={callbacks:new WeakMap,requests:[]});let n=s.callbacks.get(e);void 0===n&&s.callbacks.set(e,n=new WeakSet),n.has(i)||(n.add(i),s.requests.push({elementRef:new WeakRef(e),callbackRef:new WeakRef(i)}))}}attach(t){t.addEventListener("context-request",this.onContextRequest),t.addEventListener("context-provider",this.onContextProvider)}detach(t){t.removeEventListener("context-request",this.onContextRequest),t.removeEventListener("context-provider",this.onContextProvider)}};
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function Qe({context:t}){return(e,i)=>{const s=new WeakMap;if("object"==typeof i)return i.addInitializer((function(){s.set(this,new Xe(this,{context:t}))})),{get(){return e.get.call(this)},set(t){return s.get(this)?.setValue(t),e.set.call(this,t)},init(t){return s.get(this)?.setValue(t),t}};{e.constructor.addInitializer((e=>{s.set(e,new Xe(e,{context:t}))}));const n=Object.getOwnPropertyDescriptor(e,i);let o;if(void 0===n){const t=new WeakMap;o={get:function(){return t.get(this)},set:function(e){s.get(this).setValue(e),t.set(this,e)},configurable:!0,enumerable:!0}}else{const t=n.set;o={...n,set:function(e){s.get(this).setValue(e),t?.call(this,e)}}}return void Object.defineProperty(e,i,o)}}}
/**
 * @license
 * Copyright 2022 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function Ze({context:t,subscribe:e}){return(i,s)=>{"object"==typeof s?s.addInitializer((function(){new Ye(this,{context:t,callback:t=>{this[s.name]=t},subscribe:e})})):i.constructor.addInitializer((i=>{new Ye(i,{context:t,callback:t=>{i[s]=t},subscribe:e})}))}}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */let ti=!1;
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
!function(){if(ti)return;(new Je).attach(document.body),ti=!0}();const ei=Symbol("place"),ii=Symbol("place-consumer-registration");class si extends Rt{constructor(){super(...arguments),this.noData=!0}get place(){return this.placeInternal}set place(t){this.placeInternal=t,this.updatePlaceV2(t)}willUpdate(t){t.has("contextPlace")&&!this.placeV2&&this.placeChangedCallback(this.contextPlace,t.get("contextPlace"));const e=this.getPlace();this.noData=!(e&&this.placeHasData(e)),t.has("contextRegistration")&&this.contextRegistration?.registerPlaceConsumer(this)}disconnectedCallback(){super.disconnectedCallback(),this.contextRegistration?.unregisterPlaceConsumer(this)}placeChangedCallback(t,e){}placeHasData(t){return!0}getPlace(){return this.placeV2??this.contextPlace}async updatePlaceV2(t){const e=this.getPlace();t&&Te(t)?this.placeV2=await He(t,this):this.placeV2=t,this.placeChangedCallback(this.placeV2,e)}}p([Ze({context:ii,subscribe:!0}),wt({attribute:!1}),h("design:type",Object)],si.prototype,"contextRegistration",void 0),p([Ze({context:ei,subscribe:!0}),wt({attribute:!1}),h("design:type",Object)],si.prototype,"contextPlace",void 0),p([wt({type:Boolean,attribute:"no-data",reflect:!0}),h("design:type",Object)],si.prototype,"noData",void 0),p([Lt(),h("design:type",Object)],si.prototype,"placeV2",void 0);
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
let ni=class extends si{render(){const t=this.getPlace();if(!t||!this.placeHasData(t))return et``;const e=t.attributions||[];return et`${Ae(xe(e,this.makeAttributionHTML),et`<span class="sep">, </span>`)}`}getRequiredFields(){return["attributions"]}placeHasData(t){return!!(t.attributions&&t.attributions.length>0)}makeAttributionHTML(t){return Ue(t.provider,t.providerURI)}};ni.styles=v`
    a {
      color: inherit;
      text-decoration: inherit;
    }

    a:hover {
      text-decoration: underline;
    }
  `,ni=p([At("gmpx-place-attribution")],ni);
/**
 * @license
 * Copyright 2021 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const oi=(t,e,i)=>{for(const i of e)if(i[0]===t)return(0,i[1])();return i?.()};
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */class ri extends Event{constructor(t){super("gmpx-requesterror",{bubbles:!1,composed:!1}),this.error=t}}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */const ai={fromAttribute(t){if(null===t)return;const[e,i]=t.split(",").map((t=>Number(t.trim())));return{lat:e||0,lng:i||0}},toAttribute:t=>t?`${t.lat},${t.lng}`:null},li={fromAttribute:t=>t?.split(/\s+/).filter((t=>""!==t))??void 0,toAttribute:t=>t?.join(" ")??null};
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
class ci{constructor(t){this.capacity=t,this.map=new Map}has(t){return this.reinsertIfPresent(t),this.map.has(t)}get(t){return this.reinsertIfPresent(t),this.map.get(t)}set(t,e){if(this.delete(t),this.map.set(t,e),this.map.size>this.capacity){const[t]=this.map.keys();this.map.delete(t)}}delete(t){this.map.has(t)&&this.map.delete(t)}reinsertIfPresent(t){if(this.map.has(t)){const e=this.map.get(t);this.map.delete(t),this.map.set(t,e)}}}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
var di,pi;!function(t){t.EMPTY="EMPTY",t.LOADING="LOADING",t.LOADED="LOADED",t.ERROR="ERROR"}(pi||(pi={}));let hi=di=class extends Rt{constructor(){super(...arguments),this.autoFetchDisabled=!1,this.contextRegistration={registerPlaceConsumer:t=>{this.registerPlaceConsumer(t)},unregisterPlaceConsumer:t=>{this.unregisterPlaceConsumer(t)}},this.loadingState=pi.EMPTY,this.slotValidator=new ve(this,this.logger,["","initial-loading","error"]),this.placeConsumers=new Set,this.placeAttributions=new Set,this.placeContextProvider=new Xe(this,{context:ei})}get contextPlace(){return this.placeContextProvider.value}set contextPlace(t){this.placeContextProvider.setValue(t,!0)}render(){return oi(this.loadingState,[[pi.EMPTY,()=>et``],[pi.LOADING,()=>et`<slot name="initial-loading"></slot>`],[pi.LOADED,()=>et`<slot></slot>`],[pi.ERROR,()=>et`<slot name="error"></slot>`]])}async updated(t){if(t.has("place"))try{await this.updatePlace()}catch(t){this.handleError(t)}}async updatePlace(){if(this.loadingState=pi.LOADING,!this.place)return this.contextPlace=void 0,void(this.loadingState=pi.EMPTY);if("string"==typeof this.place?this.contextPlace=await di.placeLookup.getPlace(this.place):Te(this.place)?(this.contextPlace=await He(this.place,this),di.placeLookup.updatePlace(this.contextPlace)):(this.contextPlace=this.place,di.placeLookup.updatePlace(this.contextPlace)),"string"==typeof this.place||!this.autoFetchDisabled){let t;this.fields?.length?t=this.fields:(await 0,t=this.getConsumerFields());try{await this.contextPlace.fetchFields({fields:t})}catch(e){if(!qe(e,"fetchFields()"))throw e;this.contextPlace=await He({place_id:this.contextPlace.id}),di.placeLookup.updatePlace(this.contextPlace),await this.contextPlace.fetchFields({fields:t})}for(const t of this.placeConsumers)t.requestUpdate("contextPlace",t.contextPlace,{hasChanged:()=>!0})}this.appendAttributionIfAbsent(),this.loadingState=pi.LOADED}registerPlaceConsumer(t){this.placeConsumers.add(t),t instanceof ni&&this.placeAttributions.add(t)}unregisterPlaceConsumer(t){this.placeConsumers.delete(t),t instanceof ni&&this.placeAttributions.delete(t)}getConsumerFields(){const t=new Set;for(const e of this.placeConsumers)for(const i of e.getRequiredFields())t.add(i);return Array.from(t.values())}appendAttributionIfAbsent(){0===this.placeAttributions.size&&this.appendChild(new ni)}handleError(t){this.loadingState=pi.ERROR;const e=new ri(t);this.dispatchEvent(e)}};function ui(t,e,i){return i.placeId&&(t+=`&${e}_place_id=${i.placeId}`),i.query?t+=`&${e}=${encodeURIComponent(i.query)}`:i.location?t+=`&${e}=${i.location.lat},${i.location.lng}`:i.placeId&&(t+=`&${e}=${encodeURIComponent("Selected Place")}`),t}hi.placeLookup=new class{constructor(t,e){this.consumer=e,this.cache=new ci(t)}getPlace(t){const e=this.cache.get(t);if(e)return e;const i=async function(t,e){const{Place:i}=await Nt.importLibrary("places",e);return new i({id:t})}(t,this.consumer);return this.cache.set(t,i),i}updatePlace(t){this.cache.set(t.id,Promise.resolve(t))}}(100),p([wt({type:Boolean,attribute:"auto-fetch-disabled",reflect:!0}),h("design:type",Object)],hi.prototype,"autoFetchDisabled",void 0),p([wt({converter:li,reflect:!0}),h("design:type",Array)],hi.prototype,"fields",void 0),p([wt({type:String,hasChanged:()=>!0}),h("design:type",Object)],hi.prototype,"place",void 0),p([Qe({context:ii}),wt({attribute:!1}),h("design:type",Object)],hi.prototype,"contextRegistration",void 0),p([Lt(),h("design:type",Object)],hi.prototype,"loadingState",void 0),hi=di=p([At("gmpx-place-data-provider")],hi);let gi=class extends si{constructor(){super(...arguments),this.ariaLabel=null,this.condensed=!1,this.reversed=!1,this.variant="outlined"}render(){return et`
      <gmpx-icon-button
        .ariaLabel=${this.ariaLabel}
        .condensed=${this.condensed}
        .href=${this.getHref()}
        icon="directions"
        .variant=${this.variant}
      >
        <slot></slot>
      </gmpx-icon-button>
    `}updated(){this.role=null!=this.ariaLabel?"none":null}getRequiredFields(){return["displayName","formattedAddress","location"]}placeHasData(t){return!0}getHref(){const t=this.getPlace(),e=this.reversed?t:this.origin,i=this.reversed?this.origin:t;
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
return function(t,e){let i="https://www.google.com/maps/dir/?api=1";return t&&(i=ui(i,"origin",t)),e&&(i=ui(i,"destination",e)),i}(e?ke(e):void 0,i?ke(i):void 0)}};gi.shadowRootOptions={...si.shadowRootOptions,delegatesFocus:!0},p([wt({attribute:"aria-label",reflect:!0,type:String}),h("design:type",Object)],gi.prototype,"ariaLabel",void 0),p([wt({reflect:!0,type:Boolean}),h("design:type",Object)],gi.prototype,"condensed",void 0),p([wt({attribute:!1}),h("design:type",Object)],gi.prototype,"origin",void 0),p([wt({reflect:!0,type:Boolean}),h("design:type",Object)],gi.prototype,"reversed",void 0),p([wt({reflect:!0,type:String}),h("design:type",String)],gi.prototype,"variant",void 0),gi=p([At("gmpx-place-directions-button")],gi);
/**
 * @license
 * Copyright 2024 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
class mi{start(t,e){this.stop(),this.updateTimeout(t,e)}stop(){null!=this.timeoutId&&(clearTimeout(this.timeoutId),this.timeoutId=void 0)}updateTimeout(t,e){this.timeoutId=setTimeout((()=>{t(),this.updateTimeout(t,e)}),e)}}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */const fi={"isOpen()":6e4};function yi(t){return"opening_hours.isOpen()"===t?"isOpen()":t}function vi(t,e){switch(e){case"hasCurbsidePickup":return t.hasCurbsidePickup;case"hasDelivery":return t.hasDelivery;case"hasDineIn":return t.hasDineIn;case"hasTakeout":return t.hasTakeout;case"hasWheelchairAccessibleEntrance":return t.accessibilityOptions?.hasWheelchairAccessibleEntrance;case"isReservable":return t.isReservable;case"servesBeer":return t.servesBeer;case"servesBreakfast":return t.servesBreakfast;case"servesBrunch":return t.servesBrunch;case"servesDinner":return t.servesDinner;case"servesLunch":return t.servesLunch;case"servesVegetarianFood":return t.servesVegetarianFood;case"servesWine":return t.servesWine;default:return}}async function bi(t,e){return"isOpen()"===e?async function(t){return t&&Be(t)?await t.isOpen():void 0}(t):null}let _i=class extends si{constructor(){super(...arguments),this.poll=new mi}render(){return et`${oi(this.valueToRender,[[!0,()=>et`<slot name="true"></slot>`],[!1,()=>et`<slot name="false"></slot>`]],(()=>et``))}`}getRequiredFields(){if(!this.field)return[];const t=yi(this.field);switch(t){case"isOpen()":return["businessStatus","regularOpeningHours","utcOffsetMinutes"];case"hasWheelchairAccessibleEntrance":return["accessibilityOptions"];default:return[t]}}placeHasData(t){if(!this.field)return!1;const e=yi(this.field);return"isOpen()"===e?Be(t):null!=vi(t,e)}async getUpdateComplete(){const t=await super.getUpdateComplete();return this.asyncRenderComplete&&await this.asyncRenderComplete.promise,t}willUpdate(t){if(super.willUpdate(t),this.updateValueToRender(),t.has("field")&&(this.poll.stop(),this.field)){const t=fi[yi(this.field)];t&&this.poll.start((()=>{this.requestUpdate()}),t)}}disconnectedCallback(){super.disconnectedCallback(),this.poll.stop(),this.resetAsyncRenderPromise()}updateValueToRender(){const t=this.getPlace();if(this.resetAsyncRenderPromise(),!t||!this.field)return void(this.valueToRender=void 0);const e=yi(this.field);"isOpen()"===e?(this.asyncRenderComplete=new It,bi(t,e).then((t=>{this.valueToRender=t,this.asyncRenderComplete?.resolve()}))):this.valueToRender=function(t,e){return vi(t,e)??null}(t,e)}resetAsyncRenderPromise(){this.asyncRenderComplete?.resolve(),this.asyncRenderComplete=void 0}};
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
function $i(t){switch(t){case"url":return"googleMapsURI";case"website":return"websiteURI";default:return t}}function Ai(t,e){switch($i(e)){case"googleMapsURI":return t.googleMapsURI;case"websiteURI":return t.websiteURI;default:return}}p([wt({type:String,reflect:!0}),h("design:type",String)],_i.prototype,"field",void 0),p([Lt(),h("design:type",Object)],_i.prototype,"valueToRender",void 0),_i=p([At("gmpx-place-field-boolean")],_i);let xi=class extends si{constructor(){super(...arguments),this.hrefField="websiteURI",this.ariaLabel=null}render(){const t=this.getHref();return et`${jt(t,(()=>et`
      <a target="_blank" rel="noopener noreferrer" href=${t}
          aria-label=${this.ariaLabel??st}>
        ${jt(this.hasContentForSlot(),(()=>et`<slot></slot>`),(()=>et`${this.getDefaultLinkText(t)}`))}
      </a>
    `))}`}updated(){this.role=null!=this.ariaLabel?"none":null}getRequiredFields(){return[$i(this.hrefField)]}placeHasData(t){return null!=Ai(t,this.hrefField)}getHref(){const t=this.getPlace();return t?Ai(t,this.hrefField)??null:null}hasContentForSlot(){return!!(this.textContent?.trim()||this.children.length>0)}getDefaultLinkText(t){return"googleMapsURI"===$i(this.hrefField)?"View on Google Maps":function(t){const e=t.match(/^(https?:\/\/)?(www\.)?([^\/\?]+)/);return e&&e.length>3?e[3]:t}(t)}};xi.styles=v`
    :host(:hover) {
      text-decoration: underline;
    }

    a {
      color: inherit;
      text-decoration: inherit;
    }
  `,p([wt({type:String,reflect:!0,attribute:"href-field"}),h("design:type",String)],xi.prototype,"hrefField",void 0),p([wt({attribute:"aria-label",reflect:!0,type:String}),h("design:type",Object)],xi.prototype,"ariaLabel",void 0),xi=p([At("gmpx-place-field-link")],xi);
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
const Ei=Object.freeze({LOCATOR_BACK_BUTTON_CTA:"Back",LOCATOR_DIRECTIONS_BUTTON_LABEL:t=>`Directions to ${t}`,LOCATOR_LIST_HEADER:"Find a location near you",LOCATOR_LIST_SUBHEADING:"All locations",LOCATOR_LIST_SUBHEADING_WITH_SEARCH:"Nearest locations",LOCATOR_SEARCH_LOCATION_MARKER_TITLE:"My location",LOCATOR_SEARCH_PROMPT:"Enter your address or zip code",LOCATOR_VIEW_DETAILS_CTA:"View details",PLACE_CLEAR_ARIA_LABEL:"Clear",PLACE_CLOSED:"Closed",PLACE_CLOSED_PERMANENTLY:"Permanently closed",PLACE_CLOSED_TEMPORARILY:"Temporarily closed",PLACE_CLOSES:t=>`Closes ${t}`,PLACE_HAS_DELIVERY:"Delivery",PLACE_HAS_DINE_IN:"Dine-in",PLACE_HAS_TAKEOUT:"Takeout",PLACE_NO_DELIVERY:"No Delivery",PLACE_NO_DINE_IN:"No Dine-in",PLACE_NO_TAKEOUT:"No Takeout",PLACE_OPEN_ALWAYS:"Open 24 hours",PLACE_OPEN_NOW:"Open now",PLACE_OPENING_HOURS_DEFAULT_SUMMARY:"See opening hours",PLACE_OPENING_HOURS_ARIA_LABEL:"Weekly opening hours",PLACE_OPENS:t=>`Opens ${t}`,PLACE_OPERATIONAL:"Operational",PLACE_PHOTO_ALT:t=>`Photo of ${t||"place"}`,PLACE_PHOTO_ATTRIBUTION_PREFIX:"Photo by",PLACE_PHOTO_BACK_ARIA_LABEL:"Back",PLACE_PHOTO_NEXT_ARIA_LABEL:"Next",PLACE_PHOTO_PREV_ARIA_LABEL:"Previous",PLACE_PHOTO_TILE_ARIA_LABEL:t=>`Open photo ${t}`,PLACE_RATING_ARIA_LABEL:t=>1===t?"1 star":`${t} stars`,PLACE_REVIEWS_AUTHOR_PHOTO_ALT:t=>`Photo of ${t||"reviewer"}`,PLACE_REVIEWS_MORE:"More reviews",PLACE_REVIEWS_SECTION_CAPTION:"Most relevant",PLACE_REVIEWS_SECTION_HEADING:"Reviews by Google users",PLACE_SEARCH_ARIA_LABEL:"Search",PLACE_TYPE:t=>{if(""===t)return"";return(t[0].toUpperCase()+t.slice(1)).replace(/_/g," ")}});
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */class wi{constructor(t){this.host=t,t.addController(this)}hostConnected(){wi.connectedComponents.add(this.host)}hostDisconnected(){wi.connectedComponents.delete(this.host)}getStringLiteral(t,...e){const i=wi.translatedStringLiterals[t]??Ei[t];return"string"==typeof i?i:i(...e)}static setStringLiterals(t){for(const e of Object.keys(t))wi.translatedStringLiterals[e]=t[e];for(const t of wi.connectedComponents)t.requestUpdate()}static buildLocalizer(t){const e=new wi(t);return e.getStringLiteral.bind(e)}static reset(){wi.connectedComponents.clear(),wi.translatedStringLiterals={}}}wi.connectedComponents=new Set,wi.translatedStringLiterals={};
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
const Li=new Set(["accounting","airport","amusement_park","aquarium","art_gallery","atm","bakery","bank","bar","beauty_salon","bicycle_store","book_store","bowling_alley","bus_station","cafe","campground","car_dealer","car_rental","car_repair","car_wash","casino","cemetery","church","city_hall","clothing_store","convenience_store","courthouse","dentist","department_store","doctor","drugstore","electrician","electronics_store","embassy","fire_station","florist","funeral_home","furniture_store","gas_station","gym","hair_care","hardware_store","hindu_temple","home_goods_store","hospital","insurance_agency","jewelry_store","laundry","lawyer","library","light_rail_station","liquor_store","local_government_office","locksmith","lodging","meal_delivery","meal_takeaway","mosque","movie_rental","movie_theater","moving_company","museum","night_club","painter","park","parking","pet_store","pharmacy","physiotherapist","plumber","police","post_office","primary_school","real_estate_agency","restaurant","roofing_contractor","rv_park","school","secondary_school","shoe_store","shopping_mall","spa","stadium","storage","store","subway_station","supermarket","synagogue","taxi_stand","tourist_attraction","train_station","transit_station","travel_agency","university","veterinary_care","zoo"]);function Oi(t){switch(t){case"business_status":return"businessStatus";case"name":return"displayName";case"formatted_address":return"formattedAddress";case"place_id":return"id";case"international_phone_number":return"internationalPhoneNumber";case"geometry.location":return"location";case"geometry.location.lat":return"location.lat";case"geometry.location.lng":return"location.lng";case"formatted_phone_number":return"nationalPhoneNumber";case"plus_code.compound_code":return"plusCode.compoundCode";case"plus_code.global_code":return"plusCode.globalCode";case"rating":return"rating";case"user_ratings_total":return"userRatingCount";default:return t}}let Ci=class extends si{constructor(){super(...arguments),this.getMsg=wi.buildLocalizer(this)}render(){return et`<span>${this.getDisplayText()}</span>`}getRequiredFields(){return this.field?[(t=this.field,Oi(t).split(".")[0])]:[];var t}placeHasData(t){return!(!this.field||null==this.getFieldValue(t,this.field))}getDisplayText(){const t=this.getPlace();return t&&this.field?this.getFieldValue(t,this.field)??"":""}getFieldValue(t,e){switch(Oi(e)){case"businessStatus":return this.renderBusinessStatus(t.businessStatus);case"displayName":return t.displayName;case"formattedAddress":return t.formattedAddress;case"id":return t.id;case"internationalPhoneNumber":return t.internationalPhoneNumber;case"location":return t.location?.toString();case"location.lat":return t.location?.lat().toString();case"location.lng":return t.location?.lng().toString();case"nationalPhoneNumber":return t.nationalPhoneNumber;case"plusCode.compoundCode":return t.plusCode?.compoundCode;case"plusCode.globalCode":return t.plusCode?.globalCode;case"rating":return t.rating?.toString();case"types":return t.types&&this.getDisplayType(t.types);case"userRatingCount":return t.userRatingCount?.toString();default:return}}renderBusinessStatus(t){if(!t)return t;switch(t){case"CLOSED_PERMANENTLY":return this.getMsg("PLACE_CLOSED_PERMANENTLY");case"CLOSED_TEMPORARILY":return this.getMsg("PLACE_CLOSED_TEMPORARILY");case"OPERATIONAL":return this.getMsg("PLACE_OPERATIONAL");default:return}}getDisplayType(t){for(const e of t)if(Li.has(e))return this.getMsg("PLACE_TYPE",e);return null}};p([wt({type:String,reflect:!0}),h("design:type",String)],Ci.prototype,"field",void 0),Ci=p([At("gmpx-place-field-text")],Ci);let Si=class extends si{constructor(){super(...arguments),this.summaryOnly=!1,this.expanded=!1,this.poll=new mi,this.fontLoader=new de(this,[le.MATERIAL_SYMBOLS_OUTLINED]),this.getMsg=wi.buildLocalizer(this)}disconnectedCallback(){super.disconnectedCallback(),this.poll.stop()}willUpdate(t){super.willUpdate(t),this.poll.stop(),this.getPlace()&&this.poll.start((()=>{this.requestUpdate()}),6e4)}render(){const t=this.getPlace();if(!t)return st;if(!t.regularOpeningHours)return"OPERATIONAL"===t.businessStatus?st:et`
        <div class="closed">
          <gmpx-place-field-text field="businessStatus" .place=${t}>
          </gmpx-place-field-text>
        </div>
      `;const{weekdayDescriptions:e}=t.regularOpeningHours;let i;return i=null==t.utcOffsetMinutes?this.summaryOnly?et``:et`${this.getMsg("PLACE_OPENING_HOURS_DEFAULT_SUMMARY")}`:et`
        <gmpx-place-field-boolean field="isOpen()" .place=${t}>
          <div slot="true">${this.getOpenSummaryContent(t)}</div>
          <div slot="false">${this.getClosedSummaryContent(t)}</div>
        </gmpx-place-field-boolean>
      `,this.summaryOnly?i:et`
      <button
        aria-controls="details"
        aria-expanded=${this.expanded}
        @click=${()=>this.expanded=!this.expanded}
        type="button"
      >
        ${i}
        <span aria-hidden="true" class="icon material-symbols-outlined">
          ${this.expanded?"expand_less":"expand_more"}
        </span>
      </button>
      <div
        aria-label=${this.getMsg("PLACE_OPENING_HOURS_ARIA_LABEL")}
        .hidden=${!this.expanded}
        id="details"
        role="region"
      >
        <ul>
          ${xe(e,(t=>et`
            <li>${t}</li>
          `))}
        </ul>
      </div>
    `}getRequiredFields(){return["businessStatus","regularOpeningHours","utcOffsetMinutes"]}placeHasData(t){return!("OPERATIONAL"===t.businessStatus&&!t.regularOpeningHours)&&!(!t.businessStatus&&!t.regularOpeningHours)}getOpenSummaryContent(t){const{status:e,closePoint:i,closeDate:s}=function(t,e=new Date){if(!t.regularOpeningHours||null==t.utcOffsetMinutes)return{status:Ie.UNKNOWN};if(Ce(t.regularOpeningHours))return{status:Ie.ALWAYS_OPEN};const i=Re(t.regularOpeningHours,t.utcOffsetMinutes,e);return i.period?i.closeDate?{status:Ie.WILL_CLOSE,closeDate:i.closeDate,closePoint:i.period.close}:{status:Ie.ALWAYS_OPEN}:{status:Ie.NOT_OPEN_NOW}}(t),n=et`<span class="open">${this.getMsg("PLACE_OPEN_NOW")}</span>`;return e===Ie.ALWAYS_OPEN?et`<span class="open">${this.getMsg("PLACE_OPEN_ALWAYS")}</span>`:e===Ie.WILL_CLOSE&&Oe(s)?et`
        ${n}
        ·
        <span>${this.getMsg("PLACE_CLOSES",Le(i,s))}</span>
      `:(Ie.NOT_OPEN_NOW,n)}getClosedSummaryContent(t){const{status:e,openPoint:i,openDate:s}=function(t,e=new Date){if(!t.regularOpeningHours||null==t.utcOffsetMinutes)return{status:Me.UNKNOWN};if(Ce(t.regularOpeningHours))return{status:Me.ALREADY_OPEN};const i=Se(e,t.utcOffsetMinutes),s={status:Me.NEVER_OPEN};let n=1/0;for(const o of t.regularOpeningHours.periods){const t=Pe(o.open,i);if(!o.close)return{status:Me.ALREADY_OPEN};const r=Pe(o.close,i);if(r>=t&&e>=t&&e<r)return{status:Me.ALREADY_OPEN};if(r<t&&!(e>=r&&e<t))return{status:Me.ALREADY_OPEN};t<e&&t.setDate(t.getDate()+7);const a=t.valueOf()-e.valueOf();a<n&&(n=a,s.status=Me.WILL_OPEN,s.openPoint=o.open,s.openDate=t)}return s}(t);let n=et``;return e===Me.WILL_OPEN?n=et` · <span>${this.getMsg("PLACE_OPENS",Le(i,s))}</span>`:Me.ALREADY_OPEN,et`
      <span class="closed">${this.getMsg("PLACE_CLOSED")}</span>
      ${n}
    `}};Si.styles=v`
    button {
      align-items: center;
      background: none;
      border: none;
      color: inherit;
      cursor: pointer;
      display: flex;
      font: inherit;
      padding: 0;
    }

    span {
      display: inline-block;
    }

    ul {
      list-style-type: none;
      padding: 0;
    }

    .closed {
      color: var(--gmpx-hours-color-closed, #d50000);
    }

    .open {
      color: var(--gmpx-hours-color-open, #188038);
    }

    .icon {
      direction: inherit;
      font-size: inherit;
      margin-inline-start: 1rem;
    }
  `,p([wt({attribute:"summary-only",reflect:!0,type:Boolean}),h("design:type",Object)],Si.prototype,"summaryOnly",void 0),p([Lt(),h("design:type",Object)],Si.prototype,"expanded",void 0),Si=p([At("gmpx-place-opening-hours")],Si);
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
class Pi{get isKeyboardNavigating(){return this.isKeyboardNavigatingInternal??!1}constructor(t,e){this.host=t,this.changeCallback=e,this.mousedownEventListener=()=>{!1!==this.isKeyboardNavigatingInternal&&(this.isKeyboardNavigatingInternal=!1,this.changeCallback&&this.changeCallback(!1))},this.keydownEventListener=({key:t})=>{"Tab"!==t&&"Enter"!==t||!0!==this.isKeyboardNavigatingInternal&&(this.isKeyboardNavigatingInternal=!0,this.changeCallback&&this.changeCallback(!0))},this.host.addController(this)}hostConnected(){document.addEventListener("keydown",this.keydownEventListener),document.addEventListener("mousedown",this.mousedownEventListener)}hostDisconnected(){document.removeEventListener("keydown",this.keydownEventListener),document.removeEventListener("mousedown",this.mousedownEventListener)}}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */const Ri=1200,Ii=v`calc(${Zt} * 0.5)`;function Mi(t,e){const i=Math.ceil(t*window.devicePixelRatio);return Math.min(i,e)}function Ti(t){"Escape"===t.key&&t.stopPropagation()}let ki=class extends si{constructor(){super(...arguments),this.selectedIndex=0,this.focusController=new Pi(this,(t=>{t?this.containerElement?.classList.remove("hide-focus-ring"):this.containerElement?.classList.add("hide-focus-ring")})),this.fontLoader=new de(this,[le.GOOGLE_SANS_TEXT,le.MATERIAL_SYMBOLS_OUTLINED]),this.keydownEventListener=({key:t})=>{if(this.lightboxElement?.open)switch(t){case"ArrowLeft":this.isRTL()?this.navigateToNext():this.navigateToPrevious();break;case"ArrowRight":this.isRTL()?this.navigateToPrevious():this.navigateToNext()}},this.getMsg=wi.buildLocalizer(this)}connectedCallback(){super.connectedCallback(),document.addEventListener("keydown",this.keydownEventListener)}disconnectedCallback(){super.disconnectedCallback(),document.removeEventListener("keydown",this.keydownEventListener)}render(){const t=this.getFormattedPhotos(),e=t[this.selectedIndex],i=this.getPlace()?.displayName,s=et`
      <div class="info-card">
        <button
          aria-label=${this.getMsg("PLACE_PHOTO_BACK_ARIA_LABEL")}
          autofocus
          @click=${this.closeLightbox}
        >
          <span aria-hidden="true" class="icon material-symbols-outlined">
            ${this.isRTL()?"arrow_forward":"arrow_back"}
          </span>
        </button>
        <div class="text-container">
          ${jt(i,(()=>et`<div class="title">${i}</div>`))}
          ${jt(e?.attributions.length,(()=>et`
            <div class="caption">
              <span>${this.getMsg("PLACE_PHOTO_ATTRIBUTION_PREFIX")}</span>
              ${xe(e.attributions,(({displayName:t,uri:e})=>et`${Ue(t,e??null)} `))}
            </div>
          `))}
        </div>
      </div>
    `,n=et`
      <div class="nav-controls">
        <button
          aria-label=${this.getMsg("PLACE_PHOTO_PREV_ARIA_LABEL")}
          @click=${this.navigateToPrevious}
          .disabled=${0===this.selectedIndex}
        >
          <span aria-hidden="true" class="icon material-symbols-outlined">
            ${this.isRTL()?"chevron_right":"chevron_left"}
          </span>
        </button>
        <button
          aria-label=${this.getMsg("PLACE_PHOTO_NEXT_ARIA_LABEL")}
          @click=${this.navigateToNext}
          .disabled=${this.selectedIndex===t.length-1}
        >
          <span aria-hidden="true" class="icon material-symbols-outlined">
            ${this.isRTL()?"chevron_left":"chevron_right"}
          </span>
        </button>
      </div>
    `;return et`
      <div class="container">
        <div>${xe(t.slice(0,this.maxTiles),((t,e)=>et`
      <button
        aria-label=${this.getMsg("PLACE_PHOTO_TILE_ARIA_LABEL",e+1)}
        @click=${()=>{this.openLightbox(e)}}
        .disabled=${!t}
        part="tile"
        style=${fe({"background-image":t&&`url(${t.tileUri})`})}
      ></button>
    `))}</div>
        <dialog class="lightbox" @keydown=${Ti}>
          <div class="backdrop" @click=${this.closeLightbox}></div>
          <img
            alt=${this.getMsg("PLACE_PHOTO_ALT",i??"")}
            class="photo"
            src=${(t=>t??st)(e?.uri)}
          />
          ${s}
          ${n}
        </dialog>
      </div>
    `}updated(){!this.tileSize&&this.firstTileElement&&(this.tileSize={widthPx:this.firstTileElement.clientWidth||Ri,heightPx:this.firstTileElement.clientHeight||Ri})}getRequiredFields(){return["displayName","photos"]}placeHasData(t){return!!(t.photos&&t.photos.length>0)}getFormattedPhotos(){const t=this.getPlace();return void 0!==t&&this.tileSize?t?.photos?t.photos.map((t=>function(t,e){const i=t.widthPx/t.heightPx,s=window.innerWidth/window.innerHeight,n=e.widthPx/e.heightPx,o=i>s?{maxHeight:Mi(window.innerHeight,4800)}:{maxWidth:Mi(window.innerWidth,4800)},r=i>n?{maxHeight:Mi(e.heightPx,Ri)}:{maxWidth:Mi(e.widthPx,Ri)};return{uri:t.getURI(o),tileUri:t.getURI(r),attributions:t.authorAttributions}}(t,this.tileSize))):[]:new Array(10).fill(null)}isRTL(){return"rtl"===getComputedStyle(this).direction.toLowerCase()}async openLightbox(t){this.selectedIndex=t,await this.updateComplete,this.lightboxElement?.showModal()}closeLightbox(){this.lightboxElement?.close()}navigateToPrevious(){this.selectedIndex>0&&this.selectedIndex--}navigateToNext(){const t=this.getPlace()?.photos?.length;t&&this.selectedIndex<t-1&&this.selectedIndex++}};ki.styles=v`
    :host(:not([hidden])) {
      display: block;
    }

    .container.hide-focus-ring button:focus {
      outline: none;
    }

    a {
      color: inherit;
    }

    button {
      background: none;
      border: none;
      color: inherit;
      cursor: pointer;
      padding: 0;
    }

    button[disabled] {
      cursor: default;
    }

    [part="tile"] {
      background-color: #f5f5f5;
      background-position: center;
      background-size: cover;
      border-radius: 8px;
      display: inline-block;
      height: 134px;
      width: 142px;
    }

    /* The dialog element has a default border-width: initial (3px),
       padding: 1em, and max-height/width: calc((100% - 6px) - 2em). We remove
       the border and take the corresponding 6px out of the height/width
       calculation so it still fills the screen. */
    .lightbox {
      border-width: 0;
      color: white;
      height: 100%;
      max-height: calc(100% - 2em);
      max-width: calc(100% - 2em);
      width: 100%;
    }

    .backdrop {
      background: black;
      inset: 0;
      position: absolute;
    }

    .photo {
      inset: 0;
      margin: auto;
      max-height: 100%;
      max-width: 100%;
      position: absolute;
    }

    .icon {
      font-size: calc(${Zt} * 2);
      vertical-align: middle;
    }

    .info-card {
      background: rgba(32, 33, 36, 0.7);
      border-radius: 8px;
      display: flex;
      padding: ${Zt};
      position: absolute;
    }

    .info-card .text-container {
      flex-direction: column;
      padding: 0 ${Ii};
    }

    .info-card .title {
      font: ${se};
    }

    .info-card .caption {
      font : ${oe};
    }

    .nav-controls {
      bottom: ${Zt};
      left: 0;
      margin: 0 auto;
      position: absolute;
      right: 0;
      width: fit-content;
    }

    .nav-controls button {
      background-color: rgba(32, 33, 36, 0.7);
      border-radius: calc(${Zt} * 2);
      padding: ${Ii};
      margin: ${Ii};
    }

    .nav-controls button[disabled] {
      opacity: 0.5;
    }
  `,p([wt({attribute:"max-tiles",reflect:!0,type:Number}),h("design:type",Number)],ki.prototype,"maxTiles",void 0),p([Lt(),h("design:type",Object)],ki.prototype,"selectedIndex",void 0),p([Lt(),h("design:type",Object)],ki.prototype,"tileSize",void 0),p([Ct(".container"),h("design:type",HTMLDivElement)],ki.prototype,"containerElement",void 0),p([Ct(".lightbox"),h("design:type",HTMLDialogElement)],ki.prototype,"lightboxElement",void 0),p([Ct('[part="tile"]'),h("design:type",HTMLButtonElement)],ki.prototype,"firstTileElement",void 0),ki=p([At("gmpx-place-photo-gallery")],ki);let Ni=class extends si{constructor(){super(...arguments),this.symbol="$"}render(){return et`<span>${this.getDisplayPriceLevel()}</span>`}getRequiredFields(){return["priceLevel"]}placeHasData(t){return null!=t.priceLevel}getDisplayPriceLevel(){const t=this.getPlace();return null==t?.priceLevel?"":(s=t.priceLevel,e="number"==typeof s?s:Ne[s]??null,i=this.symbol,null==e||e<0||0===i.length?"":Array.from(i)[0].repeat(e));
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
var e,i,s}};p([wt({type:String,reflect:!0}),h("design:type",Object)],Ni.prototype,"symbol",void 0),Ni=p([At("gmpx-place-price-level")],Ni);var Di;!function(t){t.FULL="full",t.HALF="half",t.EMPTY="empty"}(Di||(Di={}));let Ui=class extends si{constructor(){super(...arguments),this.condensed=!1,this.getMsg=wi.buildLocalizer(this)}render(){const t=this.getRating();return jt(null!==t,(()=>{const e=this.condensed?[Di.FULL]:function(t){let e=Math.round(2*t);const i=[];for(;e>1;)i.push(Di.FULL),e-=2;for(e>0&&i.push(Di.HALF);i.length<5;)i.push(Di.EMPTY);return i}(t);return et`
        <span role="img" aria-label=${this.getMsg("PLACE_RATING_ARIA_LABEL",t.toFixed(1))}>
          <span aria-hidden="true">
            <span>${t.toFixed(1)}</span>
            ${xe(e,(t=>et`<span class="star-icon ${t}">&#x2605;</span>`))}
          </span>
        </span>
      `}))}getRequiredFields(){return["rating"]}placeHasData(t){return null!=t.rating}getRating(){const t=this.getPlace()?.rating;return!t||t<1||t>5?null:t}};Ui.styles=v`
    .star-icon.full {
      color: ${Kt};
    }
    .star-icon.empty {
      color: ${Xt};
    }
    .star-icon.half {
      color: ${Xt};
      position: relative;
    }
    .star-icon.half::before {
      color: ${Kt};
      content: '\\2605';
      overflow: hidden;
      position: absolute;
      width: 50%;
    }
  `,p([wt({type:Boolean,reflect:!0}),h("design:type",Object)],Ui.prototype,"condensed",void 0),Ui=p([At("gmpx-place-rating")],Ui);var Hi;!function(t){t.FULL="full",t.EMPTY="empty"}(Hi||(Hi={}));let Bi=class extends si{constructor(){super(...arguments),this.fontLoader=new de(this,[le.GOOGLE_SANS_TEXT]),this.getMsg=wi.buildLocalizer(this)}render(){const t=this.getReviews();return jt(t&&t.length,(()=>et`
      <div class="container">
        ${xe(t,this.renderOneReview.bind(this))}
      </div>
    `))}getRequiredFields(){return["reviews"]}placeHasData(t){return!!(t.reviews&&t.reviews.length>0)}renderOneReview(t){const e=t.authorAttribution,i=et`
      <div class="header">
        ${jt(e?.photoURI,(()=>et`
          <a target="_blank" href="${e?.uri??""}">
            <img class="author-photo"
                alt=${this.getMsg("PLACE_REVIEWS_AUTHOR_PHOTO_ALT",e?.displayName??"")}
                src=${e.photoURI}>
          </a>
        `))}
        <a class="author-name"
          target="_blank"
          href="${e?.uri??""}">
          ${e?.displayName??""}
        </a>
      </div>
    `,s=et`
      <div class="subheader">
        ${jt(t.rating,(()=>{return et`
          <span role="img" aria-label=${this.getMsg("PLACE_RATING_ARIA_LABEL",t.rating)}>
            <span aria-hidden="true">
              ${xe((e=t.rating,Array.from({length:5}).fill(Hi.FULL,0,e).fill(Hi.EMPTY,e)),(t=>et`<span class="star-icon ${t}">&#x2605;</span>`))}
            </span>
          </span>
        `;var e}))}
        <span class="relative-time">
          ${t.relativePublishTimeDescription??""}
        </span>
      </div>
    `;return et`
      <div class="review">
        ${i}
        ${s}
        ${jt(t.text,(()=>et`
          <div class="body">
            ${t.text}
          </div>
        `))}
      </div>
    `}getReviews(){const t=this.getPlace()?.reviews;return t?void 0===this.maxReviews?t:this.maxReviews<1?null:t.slice(0,Math.floor(this.maxReviews)):null}};Bi.styles=v`
    .container {
      color: ${Vt};
      font: ${ne};
    }
    .review {
      padding: ${te(20)};
      padding-bottom: ${te(16)};
    }
    .review:not(:last-child) {
      border-bottom: ${re};
    }
    .header, .subheader {
      align-items: center;
      display: flex;
    }
    .subheader {
      margin-top: ${te(16)};
    }
    .body {
      margin-top: ${te(8)};
    }
    .author-photo {
      display: block;
      height: ${te(32)};
    }
    .author-name {
      color: inherit;
      font: ${se};
      margin-inline-start: ${te(8)};
      text-decoration: none;
    }
    .author-name:hover {
      text-decoration: underline;
    }
    .star-icon.full {
      color: ${Kt};
    }
    .star-icon.empty {
      color: ${Xt};
    }
    .relative-time {
      color: ${Yt};
      font: ${oe};
      margin-inline-start: ${te(12)};
    }
  `,p([wt({type:Number,reflect:!0,attribute:"max-reviews"}),h("design:type",Number)],Bi.prototype,"maxReviews",void 0),Bi=p([At("gmpx-place-reviews")],Bi);
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
let zi=class extends Rt{connectedCallback(){super.connectedCallback(),this.observer=new MutationObserver((()=>{this.hidden=!!this.querySelector("[no-data]")})),this.observer.observe(this,{subtree:!0,attributeFilter:["no-data"]})}disconnectedCallback(){super.disconnectedCallback(),this.observer?.disconnect()}render(){return et`<slot></slot>`}};zi=p([At("gmpx-optional-data-container-internal")],zi);
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
class ji{constructor(t,e){this.shouldRetry=e,this.requestCacheMap=new ci(t)}get(t){return this.requestCacheMap.get(this.serialize(t))??null}set(t,e){const i=this.serialize(t);this.requestCacheMap.set(i,e),e.catch((t=>{this.shouldRetry(t)&&this.requestCacheMap.delete(i)}))}serialize(t){return JSON.stringify(t,((t,e)=>{if(e instanceof Object&&!(e instanceof Array)){const t=e,i={};for(const e of Object.keys(t).sort())i[e]=t[e];return i}return e}))}}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */function Fi(){return new ji(100,(t=>"OVER_QUERY_LIMIT"===t.code||"UNKNOWN_ERROR"===t.code))}class Wi{constructor(t){this.host=t,this.host.addController(this)}hostUpdate(){}async route(t){let e=Wi.cache.get(t);null===e&&(e=this.getService().then((e=>e.route(t))),Wi.cache.set(t,e));try{return await e}catch(t){const e=new ri(t);return this.host.dispatchEvent(e),null}}async getService(){if(!Wi.service){const{DirectionsService:t}=await Nt.importLibrary("routes",this.host);Wi.service=new t}return Wi.service}static reset(){Wi.cache=Fi(),Wi.service=void 0}}function qi(t){if(!t)return null;const{placeId:e,location:i,query:s}=ke(t);return e?{placeId:e}:i?{location:i}:s?{query:s}:null}Wi.cache=Fi();let Vi=class extends si{constructor(){super(...arguments),this.fontLoader=new de(this,[le.MATERIAL_SYMBOLS_OUTLINED]),this.directionsController=new Wi(this),this.isFetchingDirectionsData=!1}willUpdate(t){super.willUpdate(t),(t.has("origin")||t.has("travelMode"))&&this.updateDirectionsData()}placeChangedCallback(t,e){t?.id!==e?.id&&this.updateDirectionsData()}render(){const{distance:t,duration:e}=this.directionsData??{};return this.isFetchingDirectionsData||!t?et``:this.travelMode&&e?et`
      <span class="icon material-symbols-outlined">
        ${
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
function(t){switch(t){case"bicycling":return"directions_bike";case"transit":return"directions_subway";case"walking":return"directions_walk";default:return"directions_car"}}(this.travelMode)}
      </span>
      <span>${e.text}</span>
    `:et`<span>${t.text}</span>`}getRequiredFields(){return[]}placeHasData(){return null!=this.directionsData}async updateDirectionsData(){if(this.isFetchingDirectionsData)return;const t=this.getPlace(),e=qi(this.origin),i=qi(t);if(e&&i){this.isFetchingDirectionsData=!0;const t=await this.directionsController.route({origin:e,destination:i,travelMode:this.travelMode?.toUpperCase()??"DRIVING"});this.directionsData=t?.routes[0]?.legs[0],this.requestUpdate()}else this.directionsData=void 0;this.isFetchingDirectionsData=!1}};Vi.styles=v`
    .icon {
      font-size: inherit;
      line-height: inherit;
      vertical-align: bottom;
    }
  `,p([wt({attribute:"travel-mode",reflect:!0,type:String}),h("design:type",String)],Vi.prototype,"travelMode",void 0),p([wt({attribute:!1}),h("design:type",Object)],Vi.prototype,"origin",void 0),p([Lt(),h("design:type",Object)],Vi.prototype,"directionsData",void 0),Vi=p([At("gmpx-place-distance-label-internal")],Vi);
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
const Yi=Object.freeze(["x-small","small","medium","large","x-large"]),Gi=et`
  <svg width="56" height="20" fill="none" viewBox="0 0 56 20" xmlns="http://www.w3.org/2000/svg">
    <path d="m6.76 14.26c-3.62 0-6.66-2.94-6.66-6.56 0-3.62 3.04-6.56 6.66-6.56 2 0 3.43 0.78 4.5 1.81l-1.27 1.25c-0.77-0.72-1.81-1.28-3.23-1.28-2.64 0-4.71 2.13-4.71 4.77 0 2.64 2.07 4.77 4.71 4.77 1.71 0 2.69-0.69 3.31-1.31 0.51-0.51 0.85-1.25 0.98-2.26h-4.05v-1.79h5.79c0.06 0.32 0.1 0.7 0.1 1.12 0 1.34-0.37 3.01-1.55 4.19-1.16 1.21-2.63 1.85-4.58 1.85z" fill="#4285F4"/>
    <path d="m22.24 10.03c0 2.43-1.91 4.23-4.24 4.23s-4.24-1.79-4.24-4.23c0-2.45 1.9-4.23 4.24-4.23s4.24 1.78 4.24 4.23zm-1.86 0c0-1.52-1.1-2.56-2.38-2.56s-2.38 1.04-2.38 2.56c0 1.5 1.1 2.56 2.38 2.56s2.38-1.05 2.38-2.56z" fill="#EA4335"/>
    <path d="m31.74 10.03c0 2.43-1.91 4.23-4.24 4.23s-4.24-1.79-4.24-4.23c0-2.45 1.9-4.23 4.24-4.23s4.24 1.78 4.24 4.23zm-1.86 0c0-1.52-1.1-2.56-2.38-2.56s-2.38 1.04-2.38 2.56c0 1.5 1.1 2.56 2.38 2.56s2.38-1.05 2.38-2.56z" fill="#FBBC05"/>
    <path d="m40.82 6.0601v7.59c0 3.12-1.84 4.4-4.02 4.4-2.05 0-3.28-1.38-3.75-2.5l1.62-0.67c0.29 0.69 0.99 1.5 2.13 1.5 1.39 0 2.26-0.86 2.26-2.48v-0.6h-0.06c-0.42 0.51-1.22 0.96-2.22 0.96-2.11 0-4.05-1.84-4.05-4.21 0-2.38 1.94-4.24 4.05-4.24 1.01 0 1.81 0.45 2.22 0.94h0.06v-0.69h1.76zm-1.63 3.99c0-1.49-0.99-2.58-2.26-2.58-1.28 0-2.35 1.09-2.35 2.58 0 1.47 1.07 2.54 2.35 2.54 1.27 0 2.26-1.07 2.26-2.54z" fill="#4285F4"/>
    <path d="M44.4 2V14H42.54V2H44.4Z" fill="#34A853"/>
    <path d="m52.1 11.42 1.44 0.96c-0.46 0.69-1.58 1.87-3.52 1.87-2.4 0-4.19-1.86-4.19-4.23 0-2.51 1.81-4.23 3.99-4.23 2.19 0 3.26 1.74 3.62 2.69l0.19 0.48-5.65 2.34c0.43 0.85 1.1 1.28 2.05 1.28s1.59-0.45 2.07-1.16zm-4.44-1.52 3.78-1.57c-0.21-0.53-0.83-0.9-1.57-0.9-0.94 0.01-2.25 0.84-2.21 2.47z" fill="#EA4335"/>
  </svg>
`;let Ki=class extends Rt{constructor(){super(...arguments),this.autoFetchDisabled=!1,this.googleLogoAlreadyDisplayed=!1,this.size="x-large",this.travelMode="driving",this.fontLoader=new de(this,[le.GOOGLE_SANS_TEXT,le.MATERIAL_SYMBOLS_OUTLINED]),this.slotValidator=new ve(this,this.logger,["action"]),this.getMsg=wi.buildLocalizer(this),this.renderHeaderSuffixContent=()=>oi(this.size,[["small",()=>et`<slot name="action"></slot>`],["medium",()=>et`
      <gmpx-place-photo-gallery class="gallery" max-tiles="1">
      </gmpx-place-photo-gallery>
    `]]),this.renderCondensedSummary=()=>et`
    <div class="summary body">
      <div class="line">
        <gmpx-place-rating condensed></gmpx-place-rating>
        <gmpx-optional-data-container-internal>
          <span class="delimiter">·</span>
          <gmpx-place-field-text field="types"></gmpx-place-field-text>
        </gmpx-optional-data-container-internal>
        <gmpx-optional-data-container-internal>
          <span class="delimiter">·</span>
          <gmpx-place-distance-label-internal
            .origin=${this.travelOrigin}
            @gmpx-requesterror=${this.forwardRequestError}
          ></gmpx-place-distance-label-internal>
        </gmpx-optional-data-container-internal>
      </div>
    </div>
  `,this.renderSummary=()=>et`
    <div class="summary body">
      <div class="line">
        <gmpx-place-rating></gmpx-place-rating>
        <gmpx-optional-data-container-internal>
          (<gmpx-place-field-text field="userRatingCount">
          </gmpx-place-field-text>)
        </gmpx-optional-data-container-internal>
      </div>
      <div class="line">
        <gmpx-place-field-text field="types"></gmpx-place-field-text>
        <gmpx-optional-data-container-internal>
          <span class="delimiter">·</span>
          <gmpx-place-price-level></gmpx-place-price-level>
        </gmpx-optional-data-container-internal>
        <gmpx-optional-data-container-internal>
          <span class="delimiter">·</span>
          <gmpx-place-distance-label-internal
            .origin=${this.travelOrigin}
            .travelMode=${this.travelMode}
            @gmpx-requesterror=${this.forwardRequestError}
          ></gmpx-place-distance-label-internal>
        </gmpx-optional-data-container-internal>
      </div>
      <div class="line">
        <gmpx-place-opening-hours summary-only></gmpx-place-opening-hours>
      </div>
      <div class="line">
        <gmpx-optional-data-container-internal>
          <gmpx-place-field-boolean field="hasDineIn">
            <span slot="true">${this.getMsg("PLACE_HAS_DINE_IN")}</span>
            <span slot="false">${this.getMsg("PLACE_NO_DINE_IN")}</span>
          </gmpx-place-field-boolean>
        </gmpx-optional-data-container-internal>
        <gmpx-optional-data-container-internal>
          <span class="delimiter">·</span>
          <gmpx-place-field-boolean field="hasTakeout">
            <span slot="true">${this.getMsg("PLACE_HAS_TAKEOUT")}</span>
            <span slot="false">${this.getMsg("PLACE_NO_TAKEOUT")}</span>
          </gmpx-place-field-boolean>
        </gmpx-optional-data-container-internal>
        <gmpx-optional-data-container-internal>
          <span class="delimiter">·</span>
          <gmpx-place-field-boolean field="hasDelivery">
            <span slot="true">${this.getMsg("PLACE_HAS_DELIVERY")}</span>
            <span slot="false">${this.getMsg("PLACE_NO_DELIVERY")}</span>
          </gmpx-place-field-boolean>
        </gmpx-optional-data-container-internal>
      </div>
    </div>
  `,this.renderContacts=()=>et`
    <div class="section body">
      <gmpx-optional-data-container-internal>
        <div class="block row">
          <span aria-hidden="true" class="icon material-symbols-outlined">
            location_on
          </span>
          <gmpx-place-field-text field="formattedAddress">
          </gmpx-place-field-text>
        </div>
      </gmpx-optional-data-container-internal>
      <gmpx-optional-data-container-internal>
        <div class="block row">
          <span aria-hidden="true" class="icon material-symbols-outlined">
            public
          </span>
          <gmpx-place-field-link href-field="websiteURI">
          </gmpx-place-field-link>
        </div>
      </gmpx-optional-data-container-internal>
      <gmpx-optional-data-container-internal>
        <div class="block row">
          <span aria-hidden="true" class="icon material-symbols-outlined">
            call
          </span>
          <gmpx-place-field-text field="nationalPhoneNumber">
          </gmpx-place-field-text>
        </div>
      </gmpx-optional-data-container-internal>
      <gmpx-optional-data-container-internal>
        <div class="block row">
          <span aria-hidden="true" class="icon material-symbols-outlined">
            schedule
          </span>
          <gmpx-place-opening-hours></gmpx-place-opening-hours>
        </div>
      </gmpx-optional-data-container-internal>
    </div>
  `,this.renderReviews=()=>et`
    <gmpx-optional-data-container-internal>
      <div class="section">
        <div class="block">
          <span class="title-large">
            ${this.getMsg("PLACE_REVIEWS_SECTION_HEADING")}
          </span><br>
          <span class="caption">
            ${this.getMsg("PLACE_REVIEWS_SECTION_CAPTION")}
          </span><br>
        </div>
        <gmpx-place-reviews></gmpx-place-reviews>
        <gmpx-place-field-link class="button" href-field="googleMapsURI">
          <div class="label">
            <span>${this.getMsg("PLACE_REVIEWS_MORE")}</span>
            <span aria-hidden="true" class="icon material-symbols-outlined">
              open_in_new
            </span>
          </div>
        </gmpx-place-field-link>
      </div>
    </gmpx-optional-data-container-internal>
  `}willUpdate(t){t.has("size")&&!Yi.includes(this.size)&&(this.logger.error(`Value "${this.size}" for attribute "size" is invalid. Acceptable choices are ${Yi.map((t=>`"${t}"`)).join(", ")}.`),this.size="x-large")}render(){return et`
      <gmpx-place-data-provider
        .autoFetchDisabled=${this.autoFetchDisabled}
        .place=${this.place??this.contextPlace}
        @gmpx-requesterror=${this.forwardRequestError}
      >
        <div class="container">
          <div class="section block first">
            <div class="header">
              <div>
                <div class=${this.getDisplayNameClass()}>
                  <gmpx-place-field-text field="displayName">
                  </gmpx-place-field-text>
                </div>
                ${"x-small"===this.size?this.renderCondensedSummary():this.renderSummary()}
              </div>
              <div>${this.renderHeaderSuffixContent()}</div>
            </div>

            ${jt("small"!==this.size&&"x-small"!==this.size,(()=>et`
              <div><slot name="action"></slot></div>
            `))}

            ${jt("large"===this.size||"x-large"===this.size,(()=>et`
              <gmpx-place-photo-gallery class="carousel gallery">
              </gmpx-place-photo-gallery>
            `))}
          </div>

          ${jt("x-large"===this.size,(()=>et`
            ${this.renderContacts()}
            ${this.renderReviews()}
          `))}

          <gmpx-place-attribution class="section caption attribution">
          </gmpx-place-attribution>

          ${jt(!this.googleLogoAlreadyDisplayed,(()=>et`
            <div class=${"x-large"===this.size?"section":""}>
              <div class="logo">${Gi}</div>
            </div>
          `))}
        </div>
        <div slot="error">
          <div class="title-large">Oops! Something went wrong.</div>
          <div class="caption">
            Failed to load data about the specified Place.
            See the JavaScript console for technical details.
          </div>
        </div>
      </gmpx-place-data-provider>
    `}getDisplayNameClass(){return"x-small"===this.size?"title-medium":"small"===this.size?"title-large":"headline"}forwardRequestError(t){t.target&&t.target===this.dataProviderElement&&console.error(t.error);const e=new ri(t.error);this.dispatchEvent(e)}};Ki.styles=v`
    .headline {
      color: ${Vt};
      font: ${ee};
    }

    .title-large {
      color: ${Vt};
      font: ${ie};
    }

    .title-medium {
      color: ${Vt};
      font: ${se};
    }

    .body {
      color: ${Vt};
      font: ${ne};
    }

    .caption {
      color: ${Yt};
      font: ${oe};
    }

    [no-data] {
      display: none;
    }

    .container {
      background-color: ${Wt};
      overflow: auto;
    }

    .section:not(.first) {
      border-top: ${re};
    }

    .section.first > * {
      margin-bottom: ${te(12)};
    }

    .block {
      margin: ${te(18)} ${te(20)};
    }

    .header {
      display: flex;
    }

    .header > :first-child {
      flex-grow: 1;
      margin-inline-end: ${te(20)};
    }

    .header .gallery::part(tile) {
      height: ${te(80)};
      width: ${te(80)};
    }

    .summary {
      color: ${Yt};
      display: flex;
      flex-direction: column;
      margin-top: ${te(4)};
    }

    .delimiter {
      display: none;
    }

    .line > * > :not(.delimiter),
    .line > :not([hidden]):not([no-data]) ~ * > .delimiter {
      display: inline-block;
    }

    slot[name="action"] {
      display: flex;
      flex-wrap: wrap;
      gap: ${te(8)};
    }

    .carousel {
      display: flex;
      line-height: normal;
      margin-inline: ${te(-20)};
      overflow-x: auto;
      padding-inline: ${te(20)};
      white-space: nowrap;
    }

    .carousel[no-data] {
      margin-bottom: ${te(-12)};
    }

    .carousel::-webkit-scrollbar {
      background-color: ${Wt};
      width: 16px;
    }
    .carousel::-webkit-scrollbar-corner {
      background-color: ${Wt};
    }
    .carousel::-webkit-scrollbar-track {
      background-color: ${Wt};
    }
    .carousel::-webkit-scrollbar-thumb {
      background-color: #c1c1c1;
      border-radius: 16px;
      border: 4px solid ${Wt};
    }
    .carousel::-webkit-scrollbar-button {
      display: none;
    }
    .carousel::-webkit-scrollbar-thumb:hover {
      background-color: #7d7d7d;
    }

    .carousel.gallery::part(tile) {
      height: ${te(134)};
      width: ${te(142)};
    }

    .row {
      display: flex;
    }

    .row > .icon {
      color: ${Ft};
      direction: inherit;
      font-size: ${te(20)};
      margin-inline-end: ${te(20)};
    }

    .button {
      display: flex;
      justify-content: center;
      text-decoration: none;
    }

    .label {
      align-items: center;
      color: ${Ft};
      display: flex;
      font: ${se};
      margin: ${te(14)} 0;
    }

    .label > .icon {
      direction: inherit;
      font-size: ${te(20)};
      margin-inline-start: ${te(4)};
    }

    .attribution:not([no-data]) {
      display: block;
      padding: ${te(12)} ${te(20)};
    }

    .logo {
      margin: 15px ${te(20)} 10px;
    }

    [slot="error"] {
      text-align: center;
      width: 100%;
    }
  `,p([wt({attribute:"auto-fetch-disabled",reflect:!0,type:Boolean}),h("design:type",Object)],Ki.prototype,"autoFetchDisabled",void 0),p([Ze({context:ei,subscribe:!0}),wt({attribute:!1}),h("design:type",Object)],Ki.prototype,"contextPlace",void 0),p([wt({attribute:"google-logo-already-displayed",reflect:!0,type:Boolean}),h("design:type",Object)],Ki.prototype,"googleLogoAlreadyDisplayed",void 0),p([wt({type:String,hasChanged:()=>!0}),h("design:type",Object)],Ki.prototype,"place",void 0),p([wt({reflect:!0,type:String}),h("design:type",String)],Ki.prototype,"size",void 0),p([wt({attribute:"travel-mode",reflect:!0,type:String}),h("design:type",Object)],Ki.prototype,"travelMode",void 0),p([wt({attribute:!1}),h("design:type",Object)],Ki.prototype,"travelOrigin",void 0),p([Ct("gmpx-place-data-provider"),h("design:type",hi)],Ki.prototype,"dataProviderElement",void 0),Ki=p([At("gmpx-place-overview")],Ki);
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
const Xi=Object.freeze(["addressComponents","adrFormatAddress","businessStatus","displayName","formattedAddress","googleMapsURI","iconBackgroundColor","location","photos","id","plusCode","svgIconMaskURI","types","utcOffsetMinutes","viewport"]),Ji=Object.freeze(["address_component","adr_address","business_status","formatted_address","geometry","icon","icon_mask_base_uri","icon_background_color","name","photos","place_id","plus_code","type","url","utc_offset_minutes"]),Qi=.75;let Zi=class extends Rt{constructor(){super(...arguments),this.strictBounds=!1,this.disableSearch=!0,this.hideClearButton=!0,this.focusController=new Pi(this),this.fontLoader=new de(this,[le.GOOGLE_SANS_TEXT,le.MATERIAL_SYMBOLS_OUTLINED]),this.autocomplete=new It,this.getMsg=wi.buildLocalizer(this)}get value(){return this.valueInternal}willUpdate(t){t.has("disableSearch")&&this.disableSearch&&this.focusController.isKeyboardNavigating&&be()===this.searchButtonElement&&this.clearButtonElement?.focus(),t.has("hideClearButton")&&this.hideClearButton&&this.focusController.isKeyboardNavigating&&be()===this.clearButtonElement&&this.inputElement?.focus()}render(){return et`
      <div class="container">
        <input
          @input=${this.handleInput}
          .placeholder=${this.placeholder??""}
        />
        <div class="overlay">
          <button
            aria-label=${this.getMsg("PLACE_SEARCH_ARIA_LABEL")}
            class="search-button"
            @click=${this.handleSearch}
            .disabled=${this.disableSearch}
            type="button"
          >
            <span aria-hidden="true" class="icon material-symbols-outlined">
              search
            </span>
          </button>
          <button
            aria-label=${this.getMsg("PLACE_CLEAR_ARIA_LABEL")}
            class="clear-button"
            @click=${this.handleClear}
            .hidden=${this.hideClearButton}
            type="button"
          >
            <span aria-hidden="true" class="icon material-symbols-outlined">
              cancel
            </span>
          </button>
        </div>
      </div>
    `}firstUpdated(){this.initializeAutocomplete(this.inputElement)}async updated(t){if(this.autocomplete.value&&this.shouldUpdateAutocompleteOptions(t)){const t=await this.makeAutocompleteOptions();this.autocomplete.value.setOptions(t)}if(t.has("forMap")&&this.forMap){const t=await this.getMapById(this.forMap);t&&this.bindTo(t)}t.has("valueInternal")&&this.dispatchEvent(new Event("gmpx-placechange"))}async bindTo(t){(await this.autocomplete.promise).bindTo("bounds",t)}async getMapById(t){const e=this.getRootNode().getElementById(t);return"GMP-MAP"===e?.tagName?(await customElements.whenDefined("gmp-map"),e.innerMap):null}shouldUpdateAutocompleteOptions(t){return t.has("country")||t.has("locationBias")||t.has("radius")||t.has("strictBounds")||t.has("type")}async makeAutocompleteOptions(){const{country:t,locationBias:e,radius:i,strictBounds:s}=this;let n;if(e&&i){const{Circle:t}=await Nt.importLibrary("maps",this);n=new t({center:e,radius:i}).getBounds()??void 0}return{bounds:n,componentRestrictions:t?{country:t}:void 0,fields:[...Ji],strictBounds:s,types:this.type?[this.type]:[]}}async initializeAutocomplete(t){const{Autocomplete:e}=await Nt.importLibrary("places",this),i=new e(t,await this.makeAutocompleteOptions());i.addListener("place_changed",(async()=>{const t=i.getPlace();t?.place_id?(this.disableSearch=!0,this.valueInternal=await He(t,this)):await this.handleSearch()})),this.autocomplete.resolve(i)}async search(t){const{Place:e}=await Nt.importLibrary("places",this),i={textQuery:t,fields:["id"],locationBias:this.autocomplete.value?.getBounds()};let s;try{({places:s}=await e.searchByText(i))}catch(e){if(!qe(e,"searchByText()"))throw e;{const e={query:t,fields:["id"],locationBias:this.autocomplete.value?.getBounds()},i=await this.searchWithFindPlaceFromQuery(e);s=[];for(const t of i){s.push(await He(t,this));break}}}return s.length?(await s[0].fetchFields({fields:[...Xi]}),s[0]):null}async searchWithFindPlaceFromQuery(t){const{PlacesService:e}=await Nt.importLibrary("places",this),i=new e(document.createElement("div"));return new Promise(((e,s)=>{i.findPlaceFromQuery({...t,fields:We(t.fields)},((t,i)=>{t&&"OK"===i?e(t):s(i)}))}))}handleClear(){this.inputElement.value="",this.valueInternal=void 0,this.disableSearch=!0,this.hideClearButton=!0}handleInput(t){t.target.value?(this.disableSearch=!1,this.hideClearButton=!1):this.handleClear()}async handleSearch(){if(!this.disableSearch&&this.inputElement?.value){this.disableSearch=!0;try{this.valueInternal=await this.search(this.inputElement.value),this.valueInternal&&this.updateInputTextFromPlace(this.valueInternal)}catch(t){const e=new ri(t);this.dispatchEvent(e)}}}updateInputTextFromPlace(t){let e;e=t.formattedAddress&&t.displayName?t.formattedAddress.startsWith(t.displayName)?t.formattedAddress:`${t.displayName}, ${t.formattedAddress}`:t.displayName??t.formattedAddress??"",e&&(this.inputElement.value=e)}};Zi.styles=v`
    :host(:not([hidden])) {
      /* Match the default display style of <input> element. */
      display: inline-block;
    }

    .container {
      color: ${Vt};
      font: ${ne};
      position: relative;
    }

    .overlay {
      display: flex;
      inset: 0;
      justify-content: space-between;
      pointer-events: none;
      position: absolute;
    }

    .icon {
      font-size: inherit;
    }

    input {
      background-color: ${Wt};
      border: 1px solid #80868b;
      border-radius: 4px;
      color: ${Vt};
      box-sizing: border-box;
      font-family: inherit;
      font-size: inherit;
      padding: calc(${Zt} * ${Qi})
               calc(${Zt} * ${2.5});
      width: 100%;
    }

    input:focus {
      outline: 2px solid ${Ft};
    }

    input::placeholder {
      color: ${Vt};
      opacity: 0.5;
    }

    button:not([hidden]) {
      align-items: center;
      background: none;
      border: none;
      color: inherit;
      display: flex;
      font: inherit;
      padding: calc(${Zt} * ${Qi});
      pointer-events: auto;
    }

    button:enabled {
      cursor: pointer;
    }
  `,Zi.shadowRootOptions={...Rt.shadowRootOptions,delegatesFocus:!0},p([wt({converter:li,reflect:!0}),h("design:type",Array)],Zi.prototype,"country",void 0),p([wt({attribute:"for-map",reflect:!0,type:String}),h("design:type",String)],Zi.prototype,"forMap",void 0),p([wt({attribute:"location-bias",converter:ai,reflect:!0}),h("design:type",Object)],Zi.prototype,"locationBias",void 0),p([wt({reflect:!0,type:String}),h("design:type",String)],Zi.prototype,"placeholder",void 0),p([wt({reflect:!0,type:Number}),h("design:type",Number)],Zi.prototype,"radius",void 0),p([wt({attribute:"strict-bounds",reflect:!0,type:Boolean}),h("design:type",Object)],Zi.prototype,"strictBounds",void 0),p([wt({reflect:!0,type:String}),h("design:type",String)],Zi.prototype,"type",void 0),p([Lt(),h("design:type",Object)],Zi.prototype,"valueInternal",void 0),p([Lt(),h("design:type",Object)],Zi.prototype,"disableSearch",void 0),p([Lt(),h("design:type",Object)],Zi.prototype,"hideClearButton",void 0),p([Ct("input"),h("design:type",HTMLInputElement)],Zi.prototype,"inputElement",void 0),p([Ct(".clear-button"),h("design:type",HTMLButtonElement)],Zi.prototype,"clearButtonElement",void 0),p([Ct(".search-button"),h("design:type",HTMLButtonElement)],Zi.prototype,"searchButtonElement",void 0),Zi=p([At("gmpx-place-picker")],Zi);
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
const ts=Symbol("route");class es extends Rt{getRoute(){return this.route??this.contextRoute}}p([Ze({context:ts,subscribe:!0}),wt({attribute:!1}),h("design:type",Object)],es.prototype,"contextRoute",void 0),p([wt({attribute:!1}),h("design:type",Object)],es.prototype,"route",void 0);
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
let is=class extends Rt{constructor(){super(...arguments),this.travelMode="driving",this.directionsController=new Wi(this)}updated(){this.updateContextRoute()}async updateContextRoute(){if(this.route)return void(this.contextRoute=this.route);const t=ss(this.originAddress,this.originPlaceId,this.originLatLng),e=ss(this.destinationAddress,this.destinationPlaceId,this.destinationLatLng);1===t&&1===e?this.contextRoute=await this.fetchRoute():(t>1&&0!==e&&this.logger.error("Too many origins. Only one of origin-lat-lng, origin-place-id, or origin-address may be specified."),e>1&&0!==t&&this.logger.error("Too many destinations. Only one of destination-lat-lng, destination-place-id, or destination-address may be specified."),this.contextRoute=void 0)}async fetchRoute(){const t=await this.directionsController.route({origin:this.getOriginRequestObject(),destination:this.getDestinationRequestObject(),travelMode:this.travelMode?.toUpperCase()});return t?.routes?t.routes[0]:void 0}getOriginRequestObject(){return this.originLatLng?{location:this.originLatLng}:this.originPlaceId?{placeId:this.originPlaceId}:{query:this.originAddress}}getDestinationRequestObject(){return this.destinationLatLng?{location:this.destinationLatLng}:this.destinationPlaceId?{placeId:this.destinationPlaceId}:{query:this.destinationAddress}}};function ss(...t){return t.filter((t=>t)).length}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */p([Qe({context:ts}),wt({attribute:!1,hasChanged:()=>!1}),h("design:type",Object)],is.prototype,"contextRoute",void 0),p([wt({converter:ai,attribute:"destination-lat-lng",reflect:!0}),h("design:type",Object)],is.prototype,"destinationLatLng",void 0),p([wt({type:String,attribute:"destination-place-id",reflect:!0}),h("design:type",String)],is.prototype,"destinationPlaceId",void 0),p([wt({type:String,attribute:"destination-address",reflect:!0}),h("design:type",String)],is.prototype,"destinationAddress",void 0),p([wt({converter:ai,attribute:"origin-lat-lng",reflect:!0}),h("design:type",Object)],is.prototype,"originLatLng",void 0),p([wt({type:String,attribute:"origin-place-id",reflect:!0}),h("design:type",String)],is.prototype,"originPlaceId",void 0),p([wt({type:String,attribute:"origin-address",reflect:!0}),h("design:type",String)],is.prototype,"originAddress",void 0),p([wt({attribute:!1}),h("design:type",Object)],is.prototype,"route",void 0),p([wt({type:String,attribute:"travel-mode",reflect:!0}),h("design:type",Object)],is.prototype,"travelMode",void 0),is=p([At("gmpx-route-data-provider")],is);class ns{constructor(t){this.map=t,this.managedComponents=new Set}static getInstanceForMap(t){return ns.instances.has(t)||ns.instances.set(t,new ns(t)),ns.instances.get(t)}async register(t){this.managedComponents.has(t)||(this.managedComponents.add(t),await this.updateViewport())}async unregister(t){this.managedComponents.has(t)&&(this.managedComponents.delete(t),await this.updateViewport())}async updateViewport(){const t=await this.getBoundsUnion();t&&this.map.innerMap.fitBounds(t)}async getBoundsUnion(){let t=null;for(const e of this.managedComponents){const i=e.getBounds();if(i){if(!t){const{LatLngBounds:e}=await Nt.importLibrary("core");t=new e}t.union(i)}}return t}}ns.instances=new Map;
/**
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
class os{get map(){return this.deferredMap.value}get mapPromise(){return this.deferredMap.promise}constructor(t){this.host=t,this.deferredMap=new It,t.addController(this)}async hostConnected(){const t=this.getContainingGmpMap();if(t){customElements.get("gmp-map")||await customElements.whenDefined("gmp-map");const e=t;this.host.isConnected&&(this.deferredMap.resolve(e.innerMap),this.viewportManager=ns.getInstanceForMap(e))}}hostDisconnected(){this.deferredMap=new It}getContainingGmpMap(){for(const t of _e(this.host))if(t instanceof Element&&"gmp-map"===t.localName)return t;return null}}
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */let rs=class extends es{get innerMarker(){return this.innerMarkerDeferred.value}get innerMarkerPromise(){return this.innerMarkerDeferred.promise}constructor(){super(),this.waypoint="origin",this.title="",this.innerMarkerDeferred=new It,this.mapController=new os(this),this.initMarker()}async initMarker(){const{AdvancedMarkerElement:t}=await Nt.importLibrary("marker",this),e=new t;this.innerMarkerDeferred.resolve(e)}async connectedCallback(){super.connectedCallback();const t=await this.mapController.mapPromise,e=await this.innerMarkerPromise;this.isConnected&&(e.map=t)}disconnectedCallback(){super.disconnectedCallback(),this.innerMarker&&(this.innerMarker.map=null)}render(){return et`<slot @slotchange=${this.onSlotChange}></slot>`}updated(t){(t.has("waypoint")||t.has("route")||t.has("contextRoute"))&&this.updatePosition(),t.has("title")&&this.updateTitle(),t.has("zIndex")&&this.updateZIndex()}async updatePosition(){const t=await this.innerMarkerPromise,e=this.getRoute();if(!e?.legs?.length)return void(t.position=null);const i=e.legs[0],s=e.legs[e.legs.length-1];this.waypoint&&"origin"!==this.waypoint?"destination"===this.waypoint?t.position=s.end_location:this.logger.error(`Unsupported waypoint "${this.waypoint}". Waypoint must be "origin" or "destination".`):t.position=i.start_location}async updateTitle(){(await this.innerMarkerPromise).title=this.title}async updateZIndex(){(await this.innerMarkerPromise).zIndex=this.zIndex}async onSlotChange(t){const e=t.target.assignedElements()[0];if(e){(await this.innerMarkerPromise).content=e}}};p([wt({type:String,reflect:!0}),h("design:type",String)],rs.prototype,"waypoint",void 0),p([wt({type:String,reflect:!0}),h("design:type",Object)],rs.prototype,"title",void 0),p([wt({type:Number,attribute:!1}),h("design:type",Number)],rs.prototype,"zIndex",void 0),rs=p([At("gmpx-route-marker"),h("design:paramtypes",[])],rs);
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
const as=["strokeColor","strokeWeight","strokeOpacity","zIndex","invisible"];let ls=class extends es{get innerPolyline(){return this.innerPolylineDeferred.value}get innerPolylinePromise(){return this.innerPolylineDeferred.promise}constructor(){super(),this.fitInViewport=!1,this.invisible=!1,this.innerPolylineDeferred=new It,this.mapController=new os(this),this.initPolyline()}async initPolyline(){const{Polyline:t}=await Nt.importLibrary("maps",this),e=new t;this.innerPolylineDeferred.resolve(e)}async connectedCallback(){super.connectedCallback();const t=await this.innerPolylinePromise,e=await this.mapController.mapPromise;this.isConnected&&(t.setMap(e),await this.mapController.viewportManager.register(this))}disconnectedCallback(){super.disconnectedCallback(),this.mapController.viewportManager?.unregister(this),this.innerPolyline?.setMap(null)}updated(t){as.some((e=>t.has(e)))&&this.setInnerPolylineOptions(),(t.has("route")||t.has("contextRoute"))&&this.updatePath(),(t.has("fitInViewport")||this.fitInViewport&&(t.has("route")||t.has("contextRoute")))&&this.mapController.viewportManager?.updateViewport()}getBounds(){return this.fitInViewport?this.getRoute()?.bounds??null:null}async setInnerPolylineOptions(){const t={strokeColor:this.strokeColor,strokeWeight:this.strokeWeight,zIndex:this.zIndex,strokeOpacity:this.strokeOpacity,visible:!this.invisible};(await this.innerPolylinePromise).setOptions(t)}async updatePath(){let t=[];const e=this.getRoute();if(e)for(const i of e.legs)for(const e of i.steps)t=t.concat(e.path);(await this.innerPolylinePromise).setPath(t)}};
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
var cs;p([wt({attribute:"fit-in-viewport",type:Boolean,reflect:!0}),h("design:type",Object)],ls.prototype,"fitInViewport",void 0),p([wt({attribute:"invisible",type:Boolean,reflect:!0}),h("design:type",Object)],ls.prototype,"invisible",void 0),p([wt({attribute:"stroke-color",type:String,reflect:!0}),h("design:type",String)],ls.prototype,"strokeColor",void 0),p([wt({attribute:"stroke-opacity",type:Number,reflect:!0}),h("design:type",Number)],ls.prototype,"strokeOpacity",void 0),p([wt({attribute:"stroke-weight",type:Number,reflect:!0}),h("design:type",Number)],ls.prototype,"strokeWeight",void 0),p([wt({attribute:"z-index",type:Number,reflect:!0}),h("design:type",Number)],ls.prototype,"zIndex",void 0),ls=p([At("gmpx-route-polyline"),h("design:paramtypes",[])],ls);let ds=cs=class extends Rt{constructor(){super(),this.travelMode="driving",this.noPin=!1,this.zIndex=10*cs.numConstructed++}render(){return et`
      <gmpx-route-data-provider
          .destinationLatLng=${this.destinationLatLng}
          .destinationPlaceId=${this.destinationPlaceId}
          .destinationAddress=${this.destinationAddress}
          .originLatLng=${this.originLatLng}
          .originPlaceId=${this.originPlaceId}
          .originAddress=${this.originAddress}
          .route=${this.route}
          .travelMode=${this.travelMode}>
        <gmpx-route-polyline
            fit-in-viewport
            stroke-color="${"#2565cd"}"
            stroke-weight="9"
            .zIndex=${this.zIndex}>
        </gmpx-route-polyline>
        <gmpx-route-polyline
            stroke-color="${"#1faefb"}"
            stroke-weight="5"
            .zIndex=${this.zIndex+1}>
        </gmpx-route-polyline>
        <gmpx-route-marker
            waypoint="origin"
            .title=${this.originAddress??""}
            .zIndex=${this.zIndex}>
          <svg width="20" height="20" style="position: relative; top: 13px;">
            <circle cx="10" cy="10" r="6" stroke="black" stroke-width="3" 
                fill="white"/>
          </svg>
        </gmpx-route-marker>
        <gmpx-route-marker
            waypoint="destination"
            .title=${this.destinationAddress??""}
            .zIndex=${this.zIndex+1}>
          <svg width="20" height="20" style="position: relative; top: 13px;">
            <circle cx="10" cy="10" r="7" stroke="black" stroke-width="3" 
                fill="white"/>
            <circle cx="10" cy="10" r="1.8" stroke="black" stroke-width="3" 
                fill="black"/>
          </svg>
        </gmpx-route-marker>
        ${jt(!this.noPin,(()=>et`
          <gmpx-route-marker
              waypoint="destination"
              .title=${this.destinationAddress??""}
              .zIndex=${this.zIndex+2}>
          </gmpx-route-marker>`))}
      </gmpx-route-data-provider>
    `}};ds.numConstructed=0,p([wt({converter:ai,attribute:"destination-lat-lng",reflect:!0}),h("design:type",Object)],ds.prototype,"destinationLatLng",void 0),p([wt({type:String,attribute:"destination-place-id",reflect:!0}),h("design:type",String)],ds.prototype,"destinationPlaceId",void 0),p([wt({type:String,attribute:"destination-address",reflect:!0}),h("design:type",String)],ds.prototype,"destinationAddress",void 0),p([wt({converter:ai,attribute:"origin-lat-lng",reflect:!0}),h("design:type",Object)],ds.prototype,"originLatLng",void 0),p([wt({type:String,attribute:"origin-place-id",reflect:!0}),h("design:type",String)],ds.prototype,"originPlaceId",void 0),p([wt({type:String,attribute:"origin-address",reflect:!0}),h("design:type",String)],ds.prototype,"originAddress",void 0),p([wt({attribute:!1}),h("design:type",Object)],ds.prototype,"route",void 0),p([wt({type:String,attribute:"travel-mode",reflect:!0}),h("design:type",Object)],ds.prototype,"travelMode",void 0),p([wt({type:Boolean,attribute:"no-pin",reflect:!0}),h("design:type",Object)],ds.prototype,"noPin",void 0),ds=cs=p([At("gmpx-route-overview"),h("design:paramtypes",[])],ds);
/**
 * @license
 * Copyright 2020 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const{I:ps}=yt,hs=(t,e)=>void 0===e?void 0!==t?._$litType$:t?._$litType$===e,us=()=>document.createComment(""),gs=(t,e,i)=>{const s=t._$AA.parentNode,n=void 0===e?t._$AB:e._$AA;if(void 0===i){const e=s.insertBefore(us(),n),o=s.insertBefore(us(),n);i=new ps(e,o,t,t.options)}else{const e=i._$AB.nextSibling,o=i._$AM,r=o!==t;if(r){let e;i._$AQ?.(t),i._$AM=t,void 0!==i._$AP&&(e=t._$AU)!==o._$AU&&i._$AP(e)}if(e!==n||r){let t=i._$AA;for(;t!==e;){const e=t.nextSibling;s.insertBefore(t,n),t=e}}}return i},ms=(t,e,i=t)=>(t._$AI(e,i),t),fs={},ys=(t,e=fs)=>t._$AH=e,vs=t=>t._$AH,bs=t=>{t._$AP?.(!1,!0);let e=t._$AA;const i=t._$AB.nextSibling;for(;e!==i;){const t=e.nextSibling;e.remove(),e=t}},_s=t=>(t=>null!=t?._$litType$?.h)(t)?t._$litType$.h:t.strings,$s=Ht(class extends Bt{constructor(t){super(t),this.et=new WeakMap}render(t){return[t]}update(t,[e]){const i=hs(this.it)?_s(this.it):null,s=hs(e)?_s(e):null;if(null!==i&&(null===s||i!==s)){const e=vs(t).pop();let s=this.et.get(i);if(void 0===s){const t=document.createDocumentFragment();s=bt(st,t),s.setConnected(!1),this.et.set(i,s)}ys(s,[e]),gs(s,void 0,e)}if(null!==s){if(null===i||i!==s){const e=this.et.get(s);if(void 0!==e){const i=vs(e).pop();(t=>{t._$AR()})(t),gs(t,void 0,i),ys(t,[i])}}this.it=e}else this.it=void 0;return this.render(e)}});
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
let As=class extends Rt{constructor(){super(...arguments),this.columnReverse=!1,this.rowLayoutMinWidth=640,this.rowReverse=!1,this.hasRowLayout=!0,this.slotValidator=new ve(this,this.logger,["main","fixed"])}connectedCallback(){super.connectedCallback(),this.resizeObserver=new ResizeObserver((()=>{this.updateLayout()})),this.resizeObserver.observe(this)}disconnectedCallback(){super.disconnectedCallback(),this.resizeObserver?.disconnect()}willUpdate(){this.updateLayout()}render(){const t=et`
      <div class="fixed-container">
        <slot name="fixed"></slot>
      </div>
    `,e=et`
      <div class="main-container">
        <slot name="main"></slot>
      </div>
    `;return et`
    <div class="layout ${zt({column:!this.hasRowLayout,row:this.hasRowLayout})}">
      ${$s(this.hasRowLayout&&this.rowReverse||!this.hasRowLayout&&!this.columnReverse?et`${e}${t}`:et`${t}${e}`)}
    </div>
    `}updateLayout(){this.hasRowLayout=this.clientWidth>=this.rowLayoutMinWidth}};As.styles=v`
    :host(:not([hidden])) {
      display: block;
      height: 100%;
    }

    .layout {
      display: flex;
      height: 100%;
      width: 100%;
    }

    .layout.column {
      flex-direction: column;
    }

    .layout.column .fixed-container {
      height: var(--gmpx-fixed-panel-height-column-layout, 50%);
    }

    .layout.row {
      flex-direction: row;
    }

    .layout.row .fixed-container {
      width: var(--gmpx-fixed-panel-width-row-layout, 320px);
    }

    .fixed-container {
      overflow: auto;
      z-index: 1;
    }

    .main-container {
      flex: 1;
      overflow: auto;
    }
  `,p([wt({attribute:"column-reverse",reflect:!0,type:Boolean}),h("design:type",Object)],As.prototype,"columnReverse",void 0),p([wt({attribute:"row-layout-min-width",reflect:!0,type:Number}),h("design:type",Object)],As.prototype,"rowLayoutMinWidth",void 0),p([wt({attribute:"row-reverse",reflect:!0,type:Boolean}),h("design:type",Object)],As.prototype,"rowReverse",void 0),p([Lt(),h("design:type",Object)],As.prototype,"hasRowLayout",void 0),As=p([At("gmpx-split-layout")],As);
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */
const xs=(t,e)=>{const i=t._$AN;if(void 0===i)return!1;for(const t of i)t._$AO?.(e,!1),xs(t,e);return!0},Es=t=>{let e,i;do{if(void 0===(e=t._$AM))break;i=e._$AN,i.delete(t),t=e}while(0===i?.size)},ws=t=>{for(let e;e=t._$AM;t=e){let i=e._$AN;if(void 0===i)e._$AN=i=new Set;else if(i.has(t))break;i.add(t),Cs(e)}};function Ls(t){void 0!==this._$AN?(Es(this),this._$AM=t,ws(this)):this._$AM=t}function Os(t,e=!1,i=0){const s=this._$AH,n=this._$AN;if(void 0!==n&&0!==n.size)if(e)if(Array.isArray(s))for(let t=i;t<s.length;t++)xs(s[t],!1),Es(s[t]);else null!=s&&(xs(s,!1),Es(s));else xs(this,t)}const Cs=t=>{t.type==Ut&&(t._$AP??=Os,t._$AQ??=Ls)};class Ss extends Bt{constructor(){super(...arguments),this._$AN=void 0}_$AT(t,e,i){super._$AT(t,e,i),ws(this),this.isConnected=t._$AU}_$AO(t,e=!0){t!==this.isConnected&&(this.isConnected=t,t?this.reconnected?.():this.disconnected?.()),e&&(xs(this,t),Es(this))}setValue(t){if((t=>void 0===t.strings)(this._$Ct))this._$Ct._$AI(t,this);else{const e=[...this._$Ct._$AH];e[this._$Ci]=t,this._$Ct._$AI(e,this,0)}}disconnected(){}reconnected(){}}const Ps=new WeakMap,Rs=Ht(class extends Ss{render(t){return st}update(t,[e]){const i=e!==this.Y;return i&&void 0!==this.Y&&this.rt(void 0),(i||this.lt!==this.ct)&&(this.Y=e,this.ht=t.options?.host,this.rt(this.ct=t.element)),st}rt(t){if("function"==typeof this.Y){const e=this.ht??globalThis;let i=Ps.get(e);void 0===i&&(i=new WeakMap,Ps.set(e,i)),void 0!==i.get(this.Y)&&this.Y.call(this.ht,void 0),i.set(this.Y,t),void 0!==t&&this.Y.call(this.ht,t)}else this.Y.value=t}get lt(){return"function"==typeof this.Y?Ps.get(this.ht??globalThis)?.get(this.Y):this.Y?.value}disconnected(){this.lt===this.ct&&this.rt(void 0)}reconnected(){this.rt(this.ct)}}),Is=(t,e,i)=>{const s=new Map;for(let n=e;n<=i;n++)s.set(t[n],n);return s},Ms=Ht(class extends Bt{constructor(t){if(super(t),t.type!==Ut)throw Error("repeat() can only be used in text expressions")}dt(t,e,i){let s;void 0===i?i=e:void 0!==e&&(s=e);const n=[],o=[];let r=0;for(const e of t)n[r]=s?s(e,r):r,o[r]=i(e,r),r++;return{values:o,keys:n}}render(t,e,i){return this.dt(t,e,i).values}update(t,[e,i,s]){const n=vs(t),{values:o,keys:r}=this.dt(e,i,s);if(!Array.isArray(n))return this.ut=r,o;const a=this.ut??=[],l=[];let c,d,p=0,h=n.length-1,u=0,g=o.length-1;for(;p<=h&&u<=g;)if(null===n[p])p++;else if(null===n[h])h--;else if(a[p]===r[u])l[u]=ms(n[p],o[u]),p++,u++;else if(a[h]===r[g])l[g]=ms(n[h],o[g]),h--,g--;else if(a[p]===r[g])l[g]=ms(n[p],o[g]),gs(t,l[g+1],n[p]),p++,g--;else if(a[h]===r[u])l[u]=ms(n[h],o[u]),gs(t,n[p],n[h]),h--,u++;else if(void 0===c&&(c=Is(r,u,g),d=Is(a,p,h)),c.has(a[p]))if(c.has(a[h])){const e=d.get(r[u]),i=void 0!==e?n[e]:null;if(null===i){const e=gs(t,n[p]);ms(e,o[u]),l[u]=e}else l[u]=ms(i,o[u]),gs(t,n[p],i),n[e]=null;u++}else bs(n[h]),h--;else bs(n[p]),p++;for(;u<=g;){const e=gs(t,l[g+1]);ms(e,o[u]),l[u++]=e}for(;p<=h;){const t=n[p++];null!==t&&bs(t)}return this.ut=r,ys(t,l),it}});
/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: BSD-3-Clause
 */function Ts(){return new ji(10,(t=>"OVER_QUERY_LIMIT"===t.code||"UNKNOWN_ERROR"===t.code))}var ks;!function(t){t[t.GEOMETRIC=0]="GEOMETRIC",t[t.DISTANCE_MATRIX=1]="DISTANCE_MATRIX"}(ks||(ks={}));class Ns{constructor(t){this.elementForLogging=t}async computeDistances(t,e,i){const s=new Map;for(const t of e)s.set(t,{});let n=[...e];if(e.length>25){const{spherical:e}=await Nt.importLibrary("geometry",this.elementForLogging);for(const[i,n]of s.entries())n.source=ks.GEOMETRIC,n.value=e.computeDistanceBetween(t,i);const i=t=>s.get(t)?.value??1/0;n.sort(((t,e)=>i(t)-i(e))),n=n.slice(0,25)}const o={origins:[t],destinations:n,travelMode:"DRIVING",unitSystem:i};let r=Ns.cache.get(o);null==r&&(r=this.getService().then((t=>t.getDistanceMatrix(o))),Ns.cache.set(o,r));const a=await r;for(let t=0;t<a.rows[0].elements.length;t++){const e=s.get(n[t]),i=a.rows[0].elements[t];"OK"===i.status&&(e.value=i.distance.value,e.text=i.distance.text,e.source=ks.DISTANCE_MATRIX)}return e.map((t=>s.get(t)))}async getService(){if(!Ns.service){const{DistanceMatrixService:t}=await Nt.importLibrary("routes",this.elementForLogging);Ns.service=new t}return Ns.service}static reset(){Ns.cache=Ts(),Ns.service=void 0}}Ns.cache=Ts();
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
const Ds="advanced",Us="intermediate",Hs="basic";
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
const Bs=v`
  :not(:defined) {
    visibility: hidden;
  }

  :host {
    /* Override the default split layout sizes */
    --_gmpx-fixed-panel-width-row-layout: var(--gmpx-fixed-panel-width-row-layout, 28.5em);
    --_gmpx-fixed-panel-height-column-layout: var(--gmpx-fixed-panel-height-column-layout, 65%);
  }

  :host(:not([hidden])) {
    display: block;
    height: 100%;
  }

  gmpx-split-layout {
    --gmpx-fixed-panel-width-row-layout: var(--_gmpx-fixed-panel-width-row-layout);
    --gmpx-fixed-panel-height-column-layout: var(--_gmpx-fixed-panel-height-column-layout);
    background: ${Wt};
    color: ${Vt};
    font: ${ne};
  }

  a {
    color: ${Ft};
    text-decoration: none;
  }

  button {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    font: inherit;
    font-size: inherit;
    padding: 0;
  }

  #locations-panel {
    box-sizing: border-box;
    overflow-y: auto;
    padding: 0.5em;
  }

  #locations-panel-list > .header {
    padding: 1.4em 1.4em 0 1.4em;
  }

  #locations-panel-list .search-title {
    align-items: center;
    display: flex;
    font: ${ie};
    margin: 0;
  }

  #locations-panel-list .search-title .icon {
    font-size: 150%;
    margin-right: 0.2em;
  }

  #locations-panel-list gmpx-place-picker {
    margin-top: 0.8em;
    position: relative;
    width: 100%;
  }

  #locations-panel-list .section-name {
    font: ${se};
    margin: 1.8em 0 1em 1.5em;
  }

  #location-results-list .result-item {
    border-bottom: ${re};
    cursor: pointer;
    padding: 0.8em 3.5em 0.8em 1.4em;
    position: relative;
  }

  #location-results-list .result-item:first-of-type {
    border-top: ${re};
  }

  #location-results-list .result-item:last-of-type {
    border-bottom: none;
  }

  #location-results-list .selected .result-item {
    outline: 2px solid ${Ft};
    outline-offset: -2px;
  }

  #location-results-list .name {
    font: ${ie};
    margin: 0 0 0.6em 0;
  }

  #location-results-list .address {
    color: ${Yt};
    margin-bottom: 0.5em;
  }

  #location-results-list .address p {
    margin: 0;
  }

  #location-results-list gmpx-place-directions-button {
    position: absolute;
    right: 1.2em;
    top: 2.6em;
  }

  #location-results-list .distance {
    position: absolute;
    right: 0;
    text-align: center;
    top: 0.9em;
    width: 5em;
  }

  #location-results-list .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3em;
    padding-top: 0.3em;
  }

  #location-results-list {
    list-style-type: none;
    margin: 0;
    padding: 0;
  }

  #details-panel .back-button {
    align-items: center;
    color: ${Ft};
    display: flex;
    font: ${ie};
    margin: 1em 0 0 1em;
  }

  #details-panel .back-button .icon {
    font-size: 140%;
    margin-right: 0.2em;
  }

  .search-pin {
    width: 25px;
    height: 25px;
    position: relative;
    top: 15px;
  }

  .search-pin > circle {
    fill: #3367D6;
    fill-opacity: 50%;
  }
`
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */,zs={mapTypeControl:!1,maxZoom:17,streetViewControl:!1};let js=class extends Rt{constructor(){super(),this.featureSet=Ds,this.mapOptions=zs,this.internalListings=[],this.initialized=!1,this.getMsg=wi.buildLocalizer(this),this.fontLoader=new de(this,[le.GOOGLE_SANS_TEXT,le.MATERIAL_SYMBOLS_OUTLINED]),this.distanceMeasurer=new Ns(this),this.listingDistances=new Map,this.initialize()}shouldUpdate(t){return this.initialized}willUpdate(t){(t.has("listings")||t.has("initialized"))&&(this.internalListings=(this.listings??[]).map((t=>this.createInternalListing(t))),this.listingDistances.clear())}updated(t){(t.has("listings")||t.has("initialized"))&&this.updateBounds(),(t.has("mapOptions")||t.has("initialized"))&&this.mapOptions&&this.mapElement?.innerMap?.setOptions(this.mapOptions)}render(){return this.initialized?et`
      <gmpx-split-layout>
        <gmpx-overlay-layout slot="fixed">
          ${this.renderSidePanelMain()}
          ${this.renderSidePanelOverlay()}
        </gmpx-overlay-layout>
        ${this.renderMapPanel()}
      </gmpx-split-layout>
    `:st}configureFromQuickBuilder(t){this.listings=function(t){function e(t){return{label:t.label??"",defaultUri:t.defaultUrl}}return(t.locations??[]).map((t=>({title:t.title??"",addressLines:[t.address1??"",t.address2??""].filter(Boolean),position:t.coords??{lat:0,lng:0},placeId:t.placeId,actions:(t.actions??[]).map(e)})))}(t),this.featureSet=function(t){return t.capabilities?.directions?Ds:t.capabilities?.input?Us:Hs}(t),this.mapOptions=function(t){const e={...t.mapOptions??{}};return e.mapId||delete e.mapId,e}(t)}async initialize(){this.mapsCoreLibrary=await Nt.importLibrary("core",this),this.initialized=!0}createInternalListing(t){const e={place_id:t.placeId,name:t.title,formatted_address:t.addressLines?.join(" "),geometry:{location:new this.mapsCoreLibrary.LatLng(t.position)}};return{...t,placeResult:e,uniqueKey:`${t.placeId}:${t.title}`}}isIntermediateOrBetter(){return this.featureSet===Us||this.featureSet===Ds}async updateDistances(t){if(this.isIntermediateOrBetter()&&t&&this.internalListings.length){const e="US"===this.userCountry?this.mapsCoreLibrary.UnitSystem.IMPERIAL:this.mapsCoreLibrary.UnitSystem.METRIC,i=await this.distanceMeasurer.computeDistances(t,this.internalListings.map((t=>t.position)),e);for(let t=0;t<i.length;t++)this.listingDistances.set(this.internalListings[t],i[t])}else this.listingDistances.clear();this.requestUpdate()}updateSearchLocation(t){const e=t.target.value;if(this.searchLocation=e??void 0,e?.addressComponents)for(const t of e.addressComponents)if(t.types.indexOf("country")>=0){this.userCountry=t.shortText??void 0;break}this.updateBounds(),this.updateDistances(e?.location)}selectLocation(t){return this.selectedListing!==t&&(this.selectedListing=t,!0)}async updateBounds(){if(!this.internalListings.length)return;const t=new this.mapsCoreLibrary.LatLngBounds;this.searchLocation?.location&&t.extend(this.searchLocation.location);for(const e of this.internalListings)t.extend(e.position);this.mapElement?.innerMap?.fitBounds(t)}renderSidePanelOverlay(){return this.featureSet===Ds?et`
          <div slot="overlay" id="details-panel">
            <button class="back-button"
                @click=${()=>this.overlayLayout?.hideOverlay()}>
              <span class="icon material-symbols-outlined">arrow_back</span>
              ${this.getMsg("LOCATOR_BACK_BUTTON_CTA")}
            </button>
            <gmpx-place-overview .place=${this.detailsPlaceId} google-logo-already-displayed>
            </gmpx-place-overview>
          </div>`:st}renderListItem(t){const e=this.listingDistances.get(t),i=e?.text&&e.source===ks.DISTANCE_MATRIX?e.text:st,s=[];if(this.featureSet===Ds){const e=()=>{t.placeId&&(this.detailsPlaceId=t.placeId,this.overlayLayout?.showOverlay())};s.push(et`
          <gmpx-icon-button class="view-details" @click=${e}>
            ${this.getMsg("LOCATOR_VIEW_DETAILS_CTA")}
          </gmpx-icon-button>`)}for(const e of t.actions??[])s.push(et`
          <gmpx-icon-button icon="open_in_new" .href=${e.defaultUri??st}>
            ${e.label}
          </gmpx-icon-button>`);const n=()=>{this.selectLocation(t)&&this.selectedListing&&!this.searchLocation&&this.mapElement?.innerMap?.panTo(this.selectedListing.position)};return et`
      <li @click=${n}
          class=${zt({selected:t===this.selectedListing})}
          ${Rs((e=>{t.listingElement=e}))}>
        <gmpx-place-data-provider auto-fetch-disabled
            .place=${t.placeResult}>
          <div class="result-item">
            <button class="select-location" @click=${t=>{n(),t.stopPropagation()}}>
              <div class="name">
                <gmpx-place-field-text field="displayName"></gmpx-place-field-text>
              </div>
            </button>
            <div class="address">
              ${(t.addressLines??[]).map((t=>et`<p>${t}</p>`))}
            </div>
            <div class="actions">
              ${Ae(s,et``)}
            </div>
            <div class="distance">${i}</div>
            <gmpx-place-directions-button condensed
                .ariaLabel=${this.getMsg("LOCATOR_DIRECTIONS_BUTTON_LABEL",t.title)}
                .origin=${this.searchLocation?.location??void 0}>
            </gmpx-place-directions-button>
          </div>
        </gmpx-place-data-provider>
      </li>`}renderSidePanelMain(){let t=this.internalListings,e=this.getMsg("LOCATOR_LIST_SUBHEADING");if(this.listingDistances.size>0){e=this.getMsg("LOCATOR_LIST_SUBHEADING_WITH_SEARCH");const i=this.internalListings.filter((t=>this.listingDistances.get(t)?.source===ks.DISTANCE_MATRIX)),s=this.internalListings.filter((t=>this.listingDistances.get(t)?.source!==ks.DISTANCE_MATRIX)),n=t=>this.listingDistances.get(t)?.value??1/0,o=(t,e)=>n(t)-n(e);t=[...i.sort(o),...s.sort(o)]}const i=this.featureSet===Hs?st:et`
        <div class="header">
          <div class="search-title">
            <span class="icon material-symbols-outlined">distance</span>
            ${this.getMsg("LOCATOR_LIST_HEADER")}
          </div>
          <gmpx-place-picker for-map="main-map" type="geocode"
              .placeholder=${this.getMsg("LOCATOR_SEARCH_PROMPT")}
              @gmpx-placechange=${this.updateSearchLocation}>
          </gmpx-place-picker>
        </div>
    `;return et`
        <div slot="main" id="locations-panel">
          <div id="locations-panel-list">
            ${i}
            <div class="section-name">
              ${e} (${t.length})
            </div>
            <div class="results">
              <ul id="location-results-list">
                ${Ms(t,(t=>t.uniqueKey),(t=>this.renderListItem(t)))}
              </ul>
            </div>
          </div>
        </div>`}renderSearchMarker(){return this.isIntermediateOrBetter()&&this.searchLocation?.location?et`
          <gmp-advanced-marker
              .position=${this.searchLocation.location}
              title="${this.getMsg("LOCATOR_SEARCH_LOCATION_MARKER_TITLE")}">
            <svg viewbox="0 0 100 100" class="search-pin">
              <circle cx="50" cy="50" r="50"></circle>
            </svg>
          </gmp-advanced-marker>`:st}renderMapMarker(t){return et`
        <gmp-advanced-marker
            .position=${t.position}
            .title=${t.title}
            .zIndex=${100}
            gmp-clickable @gmp-click=${()=>{this.selectLocation(t);const e=t.listingElement;e&&e.scrollIntoView({behavior:"smooth",block:"nearest"})}}></gmp-advanced-marker>`}renderMapDirections(){const t=this.searchLocation?.location,e=this.selectedListing?.position;return this.featureSet===Ds&&t&&e?et`
      <gmpx-route-overview no-pin
          .originLatLng=${t}
          .destinationLatLng=${e}>
      </gmpx-route-overview>`:st}renderMapPanel(){return et`
        <gmp-map slot="main" id="main-map" .mapId=${this.mapId??st}>
          ${this.renderMapDirections()}
          ${Ms(this.internalListings,(t=>t.uniqueKey),(t=>this.renderMapMarker(t)))}
          ${this.renderSearchMarker()}
        </gmp-map>`}};js.styles=Bs,p([wt({attribute:"feature-set",reflect:!0}),h("design:type",String)],js.prototype,"featureSet",void 0),p([wt({attribute:"map-id",reflect:!0}),h("design:type",String)],js.prototype,"mapId",void 0),p([wt({attribute:!1}),h("design:type",Array)],js.prototype,"listings",void 0),p([wt({attribute:!1}),h("design:type",Object)],js.prototype,"mapOptions",void 0),p([Lt(),h("design:type",Array)],js.prototype,"internalListings",void 0),p([Lt(),h("design:type",Object)],js.prototype,"selectedListing",void 0),p([Lt(),h("design:type",Object)],js.prototype,"searchLocation",void 0),p([Lt(),h("design:type",String)],js.prototype,"detailsPlaceId",void 0),p([Lt(),h("design:type",Object)],js.prototype,"initialized",void 0),p([Ct("gmpx-overlay-layout"),h("design:type",Function)],js.prototype,"overlayLayout",void 0),p([Ct("gmp-map"),h("design:type",Object)],js.prototype,"mapElement",void 0),js=p([At("gmpx-store-locator"),h("design:paramtypes",[])],js);
/**
 * @license
 * Copyright 2023 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
const{setStringLiterals:Fs}=wi;export{Nt as APILoader,ue as IconButton,$e as OverlayLayout,ni as PlaceAttribution,hi as PlaceDataProvider,gi as PlaceDirectionsButton,_i as PlaceFieldBoolean,xi as PlaceFieldLink,Ci as PlaceFieldText,Si as PlaceOpeningHours,Ki as PlaceOverview,ki as PlacePhotoGallery,Zi as PlacePicker,Ni as PlacePriceLevel,Ui as PlaceRating,Bi as PlaceReviews,is as RouteDataProvider,rs as RouteMarker,ds as RouteOverview,ls as RoutePolyline,As as SplitLayout,js as StoreLocator,Fs as setStringLiterals,d as suggestValidationAction};
