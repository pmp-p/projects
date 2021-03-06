/*
 * Copyright (C) 2019 Paul PENY "pmp-p"
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


package {{ cookiecutter.bundle }}.{{ cookiecutter.module_name }};
// also {{ cookiecutter.bundle|replace('.', '/') }}/{{ cookiecutter.module_name }} in rmipython.c
// also {{ cookiecutter.bundle|replace('.', '_') }}_{{ cookiecutter.module_name }} in pythonsupport.c
// also  "{{ cookiecutter.bundle }}" for TAG


import androidx.annotation.Keep;
import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
//import android.os.Build;
import android.view.View;
//import java.util.Locale;


//implementation 'androidx.constraintlayout:constraintlayout:1.1.3'
//import androidx.constraintlayout.widget.ConstraintLayout ;
//import androidx.constraintlayout.widget.ConstraintSet;
import android.widget.RelativeLayout;


import android.util.Log;

import android.content.Context;
import android.content.pm.PackageManager;
import android.content.pm.ApplicationInfo;


import java.util.Map;

import java.lang.reflect.AccessibleObject;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Modifier;

import java.util.List;
import java.util.ArrayList;

import java.lang.reflect.Type;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;



import android.app.ActivityManager;
import android.content.pm.ConfigurationInfo;

// ------------------- a surface for jni libs ------------------------------
//inputs
import android.view.KeyEvent ;
import android.view.MotionEvent;

//display
import android.view.Surface;

//import android.view.SurfaceView;
import android.view.SurfaceHolder;


// ==================================================================

class Window

extends android.view.SurfaceView

implements SurfaceHolder.Callback

{
    private MainActivity _host = null;

    public Window(MainActivity host) {
        super((Context) host);
        _host = host;

        getHolder().addCallback(this);

        this.setOnHoverListener( _host );

    }


    @Override
    public void surfaceCreated(SurfaceHolder holder) {
        Log.i(MainActivity.TAG, "window.surfaceCreated()");
    }

    public void surfaceChanged(SurfaceHolder holder, int format, int w, int h) {
        Log.d(
            MainActivity.TAG,
            "window.surfaceChanged->nativeSetSurface(surface) " +
            w + "x" + h);
        MainActivity.nativeSetSurface(holder.getSurface());
    }

    public void surfaceDestroyed(SurfaceHolder holder) {
        Log.d(MainActivity.TAG, "window.surfaceDestroyed->nativeSetSurface(null)");
        MainActivity.nativeSetSurface(null);
    }

}



//https://developer.android.com/reference/android/view/KeyEvent


// ----------------------- an empty application ---------------------------------

public class MainActivity

extends AppCompatActivity

implements View.OnClickListener, View.OnHoverListener

{
    public static final String PYTHON = "python3.9";
    public static final String TAG = "{{ cookiecutter.bundle }}";
    private static final String onuithread = "python3.dispatch('[\"onui\", \"\"]')";

    private static String HOME;
    private static String APK;
    private static String LIB;

    public String py_jobs = "";

    Gson gson = new Gson();

    public Window sv;

    // Application Context and ui layout, everything android goes by there
    public static HPyContext __main__ = null;


    public static JavaSpace jspy = new JavaSpace();

    static {
        System.loadLibrary("rmipython");
    }

//============================================================

    // things hard to do yet from Python or C

    public static native void nativeSetSurface(Surface jsurface);



    // GLES surface
    private boolean hasGLES20() {
        ActivityManager am = (ActivityManager)getSystemService(Context.ACTIVITY_SERVICE);
        ConfigurationInfo info = am.getDeviceConfigurationInfo();
        return info.reqGlEsVersion >= 0x20000;
    }

    java.util.Locale getCurrentLocale(Context context){
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.N){
            return context.getResources().getConfiguration().getLocales().get(0);
        } else{
            //deprecated
            return context.getResources().getConfiguration().locale;
        }
    }

/*
https://stackoverflow.com/questions/35789693/android-get-device-country-code

private static String getDeviceCountryCode(Context context) {
    String countryCode;

    // try to get country code from TelephonyManager service
    TelephonyManager tm = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
    if(tm != null) {
        // query first getSimCountryIso()
        countryCode = tm.getSimCountryIso();
        if (countryCode != null && countryCode.length() == 2)
            return countryCode.toLowerCase();

        if (tm.getPhoneType() == TelephonyManager.PHONE_TYPE_CDMA) {
            // special case for CDMA Devices
            countryCode = getCDMACountryIso();
        } else {
            // for 3G devices (with SIM) query getNetworkCountryIso()
            countryCode = tm.getNetworkCountryIso();
        }

        if (countryCode != null && countryCode.length() == 2)
            return countryCode.toLowerCase();
    }

    // if network country not available (tablets maybe), get country code from Locale class
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
        countryCode = context.getResources().getConfiguration().getLocales().get(0).getCountry();
    } else {
        countryCode = context.getResources().getConfiguration().locale.getCountry();
    }

    if (countryCode != null && countryCode.length() == 2)
        return  countryCode.toLowerCase();

    // general fallback to "us"
    return "us";
}
*/

    public Window make_window() {
        if (hasGLES20() ){
            Log.i(MainActivity.TAG," == GL/ES 2.0 avail ==");
        } else {
            Log.i(MainActivity.TAG," == Fallback to GL/ES 1.0 ==");
        }


        Window nwin = new Window(this);
        jspy.expose(nwin);
        return nwin;
    }

    public String viewport(View view) {
        jspy.push("class", "surface" );
        jspy.push("x", (int)view.getX() );
        jspy.push("y", (int)view.getY() );
        jspy.push("width", (int)view.getWidth() );
        jspy.push("height", (int)view.getHeight() );

        String result = jspy.flush_json() ;
        Log.v(MainActivity.TAG, "surface:" + result );
        return result;
    }


    public int get_x(View view) {
        return (int)view.getX();
    }

    public int get_y(View view) {
        return (int)view.getY();
    }

    // =============== input and motion  events  ===============================
    public static boolean input_accept = true;
    public static boolean input_grabbed = false;


    @Override
    public boolean onHover(View v, MotionEvent event) {
        String etype = "over";
        switch (event.getAction()) {
            case MotionEvent.ACTION_HOVER_MOVE:
                break;

            case MotionEvent.ACTION_HOVER_ENTER:
                etype = "enter";
                //_host.input_grabbed = true;
                input_grabbed = true;
                break;

            case MotionEvent.ACTION_HOVER_EXIT:
                etype = "leave";
                input_grabbed = false;
                //_host.input_grabbed = false;
                break;
        }

        App("onmouse", v.getId(), etype, (int)event.getX(), (int)event.getY() );
        return false;
    }


    @Override
    public void onClick(View v) {
      // default method for handling onClick Events..
        Log.v(MainActivity.TAG, "onClick :" + v.getId());
        App("on_event", v.getId() );
    }


    private static final int INVALID_POINTER_ID = -1;
    private int pointer_id = INVALID_POINTER_ID;


    @Override
    public boolean onKeyDown(int keyCode, final KeyEvent event) {

        if (input_grabbed) {
            Log.i(MainActivity.TAG, String.format("GRAB key Down %d %b", keyCode, input_grabbed));
            return true;
        }
        Log.i(MainActivity.TAG, String.format("PASS key Down %d %b", keyCode, input_grabbed));
        /*
        if (input_accept && nativeKey(keyCode, 1, event.getUnicodeChar())) {
            return true;
        } else {
            return super.onKeyDown(keyCode, event);
        }
        */
        return super.onKeyDown(keyCode, event);
    }

    @Override
    public boolean onKeyUp(int keyCode, final KeyEvent event) {


        if (input_grabbed) {
            Log.i(MainActivity.TAG, String.format("GRAB key UP   %d %b", keyCode, input_grabbed));
            return true;
        }

        // block escape in games
        if ( (keyCode==4) && input_grabbed )
            return false;

        Log.i(MainActivity.TAG, String.format("PASS key UP   %d %b", keyCode, input_grabbed));

        /*
        if (input_accept && nativeKey(keyCode, 0, event.getUnicodeChar())) {
            return true;
        } else {
            return super.onKeyUp(keyCode, event);
        }
        */
        return super.onKeyUp(keyCode, event);
    }

   // @Override
    public boolean onFling(MotionEvent e1, MotionEvent e2, float velocityX, float velocityY) {
        Log.i(MainActivity.TAG, "fling");
        //scroller.fling(currentX, currentY, velocityX / SCALE, velocityY / SCALE, minX, minY, maxX, maxY);
        //postInvalidate();
        return true;
    }

    @Override
    public boolean onTouchEvent(final MotionEvent event) {
        int action = event.getAction() & MotionEvent.ACTION_MASK;
        int sdlAction = -1;
        int pointerId = -1;
        int pointerIndex = -1;

        switch ( action ) {
            case MotionEvent.ACTION_MOVE:
                sdlAction = 2;
                break;

            case MotionEvent.ACTION_DOWN:
            case MotionEvent.ACTION_POINTER_DOWN:
                sdlAction = 0;
                break;

            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_POINTER_UP:
                sdlAction = 1;

                break;
        }

        for ( int i = 0; i < event.getPointerCount(); i++ ) {
            int screenX = (int)event.getX(i);
            int screenY = (int)event.getY(i);

            String modata = String.format(
                "{'e':'mouse', 'id':%d, 'action':%d," +
                "'x':%d, 'y':%d,",
                    event.getPointerId(i),
                    sdlAction,
                    screenX,
                    screenY
            );

            App("oncursor", modata );
            //Log.i(MainActivity.TAG, modata);
        }

        if (input_accept == false)
            return true;



        // http://android-developers.blogspot.com/2010/06/making-sense-of-multitouch.html
        switch ( action  & MotionEvent.ACTION_MASK ) {
            case MotionEvent.ACTION_DOWN:
            case MotionEvent.ACTION_MOVE:
            case MotionEvent.ACTION_UP:
                pointerIndex = event.findPointerIndex(pointer_id);
                break;
            case MotionEvent.ACTION_POINTER_DOWN:
            case MotionEvent.ACTION_POINTER_UP:
                pointerIndex = (event.getAction() & MotionEvent.ACTION_POINTER_INDEX_MASK)
                    >> MotionEvent.ACTION_POINTER_INDEX_SHIFT;
                if ( action == MotionEvent.ACTION_POINTER_UP ) {
                    pointerId = event.getPointerId(pointerIndex);
                    if ( pointerId == pointer_id )
                        pointer_id = event.getPointerId(pointerIndex == 0 ? 1 : 0);
                }
                break;
        }

        if ( sdlAction >= 0 ) {

            for ( int i = 0; i < event.getPointerCount(); i++ ) {

                if ( pointerIndex == -1 || pointerIndex == i ) {

                    /*
                    SDLSurfaceView.nativeMouse(
                            (int)event.getX(i),
                            (int)event.getY(i),
                            sdlAction,
                            event.getPointerId(i),
                            (int)(event.getPressure(i) * 1000.0),
                            (int)(event.getSize(i) * 1000.0));
                    */
                }

            }

        }

        return true;
    };







// ===========================================================


    public native String stringFromJNI();

    public static native String PyRun(String jstring_code);

    public static int jobs_processing = 0;
    public ArrayList<String> outq;
    public ArrayList<String> appq;

    private ArrayList get_array(String json) {
        return gson.fromJson(json , ArrayList.class );
    }


    public native void jnionCreate(
        String jstring_tag,
        String jstring_ver,
        String jstring_apk,
        String jstring_lib,
        String jstring_home);

    public native void VMstart();
    public native void VMresume();
    public native void VMpause();
    public native void VMstop();

    public void App(Object ...args){
            appq.add( gson.toJson(args)) ;
    }


    int hour = 0;
    int minute = 0;
    int second = 0;

    int steps = 0;


    android.widget.TextView tickView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        Log.v(MainActivity.TAG, " ============== onCreate : Java begin ================");

        PackageManager pm = getPackageManager();

        try {
            // or is it Context.getApplicationInfo().sourceDir ?
            ApplicationInfo ai = pm.getApplicationInfo(getApplicationContext().getPackageName(), 0);
            APK = ai.publicSourceDir;
            LIB = ai.nativeLibraryDir;
            Log.v(MainActivity.TAG, "APK : "+ APK );
            java.io.File file =  new java.io.File( getApplicationContext().getFilesDir().getPath() );
            HOME = file.getParent() ;
            Log.v(MainActivity.TAG, "HOME : " + HOME  );
        } catch (Throwable x) {
            Log.e(MainActivity.TAG, "cannot locate APK");
        }


        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_main);


        View main = findViewById(android.R.id.content).getRootView() ;
        main.setId( System.identityHashCode(main) );
        main.setOnHoverListener( this );

        android.widget.RelativeLayout ui;
        ui = (android.widget.RelativeLayout ) findViewById(R.id.Applications);

        tickView = new android.widget.TextView(this);
        ui.addView(tickView);



        outq  = new ArrayList<String>();
        appq  = new ArrayList<String>();

        if (ui!=null) {
            __main__ = jspy.new_context(TAG, this, ui);
            jspy.expose(main);

            // a simple test for javaspace
            // jspy.ffi_call("java.lang.System", null, "getProperty" , "java.specification.version");


        }
        Log.v(MainActivity.TAG, " ============== onCreate : Java end ================");
        jnionCreate(MainActivity.TAG, PYTHON, APK, LIB, HOME);
    }

    @Override
    public void onResume() {
        super.onResume();
        hour = minute = second = 0;
        ((android.widget.TextView)findViewById(R.id.hellojniMsg)).setText(stringFromJNI());
        Log.v(MainActivity.TAG, " ============== onResume : Java Begin ================");
        Log.i(MainActivity.TAG, "JAVA LOCALE : " + getCurrentLocale(getApplicationContext()) );
        VMstart();
        Log.v(MainActivity.TAG, " ============== onResume : Java End ================");
    }

    @Override
    public void onPause () {
        super.onPause();
        VMstop();
    }

    /*
     * A function calling from JNI to update current timer
     */
    @Keep
    private void updateTimer() {

        if (outq.size()>0) {
            //android.util.Log.i(MainActivity.TAG, "AIO java->python");

            while ( outq.size()>0 ) {
                String retjson = outq.remove(0).toString();
                MainActivity.this.PyRun("aio.step("+ retjson +")");
            }
        }

        if (appq.size()>0) {
            //android.util.Log.i(MainActivity.TAG, "Events java->python");

            while ( appq.size()>0 ) {
                PyRun("python3.dispatch("+appq.remove(0)+")");
            }
        }

        // if busy don't multiply pending runnables.

        if (jobs_processing>0) {
            //android.util.Log.i(MainActivity.TAG, "AIO UI is busy");
            return ;
        }

        // not busy ? time to do ui stuff

        MainActivity.this.py_jobs = PyRun(onuithread);

        if (MainActivity.__main__ != null) {
            if (MainActivity.this.py_jobs.length()>4)
                jobs_processing = 1;
        }

        ++second;
        if(second >= 60) {
            ++minute;
            second -= 60;
            if(minute >= 60) {
                ++hour;
                minute -= 60;
            }
        }

        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                String ticks = "" + MainActivity.this.hour + ":" +
                        MainActivity.this.minute + ":" +
                        MainActivity.this.second;

                MainActivity.this.tickView.setText(ticks);

                // not ready yet or empty work queue
                if (jobs_processing==0)
                    return;

                // there are jobs, exec them in UI thread
                try {
                    android.util.Log.i(MainActivity.TAG, "JOBS : " + MainActivity.this.py_jobs);
                    for (String retjson: jspy.Calls(get_array(MainActivity.this.py_jobs)) ) {
                        outq.add( retjson );
                    }
                }
                catch (IllegalStateException e) {
                    android.util.Log.e(MainActivity.TAG, MainActivity.this.py_jobs);
                }

                // clear the work queue ( it serves also as busy marker for calling thread)
                MainActivity.this.py_jobs = "";
                jobs_processing = 0;

            }
        });

    }




}




































//
