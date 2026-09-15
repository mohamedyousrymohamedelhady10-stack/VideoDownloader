package com.mohamed.videodownloader;

import android.app.Activity;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.content.ContentValues;
import android.content.ContentResolver;
import android.net.Uri;
import android.view.View;
import android.widget.*;

import com.chaquo.python.Python;
import com.chaquo.python.PyObject;
import com.arthenica.ffmpegkit.FFmpegKit;
import com.arthenica.ffmpegkit.ReturnCode;

import java.io.*;
import org.json.JSONObject;

public class MainActivity extends Activity {

    EditText url;
    Button download;
    ProgressBar progress;
    TextView status;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_main);

        url = findViewById(R.id.url);
        download = findViewById(R.id.download);
        progress = findViewById(R.id.progress);
        status = findViewById(R.id.status);

        download.setOnClickListener(v -> startDownload());
    }

    private void startDownload() {

        String link = url.getText().toString().trim();

        if (link.isEmpty()) {
            status.setText("⚠️ الصق رابط الفيديو أولًا.");
            return;
        }

        if (!link.startsWith("http://") &&
                !link.startsWith("https://")) {

            status.setText("⚠️ الرابط غير صحيح.");
            return;
        }

        download.setEnabled(false);
        progress.setVisibility(View.VISIBLE);

        status.setText("جاري تحليل الرابط والتحميل...");

        new Thread(() -> {

            File workDir =
                    new File(getCacheDir(), "download");

            try {

                workDir.mkdirs();

                Python py = Python.getInstance();

                PyObject module =
                        py.getModule("downloader");

                String json =
                        module.callAttr(
                                "download",
                                link,
                                workDir.getAbsolutePath()
                        ).toJava(String.class);

                JSONObject data =
                        new JSONObject(json);

                String mode =
                        data.getString("mode");

                String title =
                        data.getString("title");

                File source;

                if ("single".equals(mode)) {

                    source =
                            new File(
                                    data.getString("video")
                            );

                    saveToDownloads(
                            source,
                            title
                    );

                    finishSuccess(workDir);

                    return;
                }

                File video =
                        new File(
                                data.getString("video")
                        );

                File audio =
                        new File(
                                data.getString("audio")
                        );

                File output =
                        new File(
                                workDir,
                                "final_" +
                                System.currentTimeMillis() +
                                ".mp4"
                        );

                runOnUiThread(() ->
                        status.setText(
                                "جاري دمج الفيديو والصوت..."
                        )
                );

                String command =
                        "-y -i \"" +
                        video.getAbsolutePath() +
                        "\" -i \"" +
                        audio.getAbsolutePath() +
                        "\" -map 0:v:0 -map 1:a:0 " +
                        "-c:v copy -c:a aac \"" +
                        output.getAbsolutePath() +
                        "\"";FFmpegKit.executeAsync(
                        command,
                        session -> {

                            if (ReturnCode.isSuccess(
                                    session.getReturnCode()
                            )) {

                                try {

                                    saveToDownloads(
                                            output,
                                            title
                                    );

                                    finishSuccess(
                                            workDir
                                    );

                                } catch (Exception e) {

                                    showError(
                                            e.getMessage()
                                    );
                                }

                            } else {

                                showError(
                                        "فشل دمج الفيديو والصوت."
                                );
                            }
                        }
                );

            } catch (Exception e) {

                showError(
                        e.getMessage()
                );
            }

        }).start();
    }

    private void saveToDownloads(
            File source,
            String title
    ) throws Exception {

        String safe =
                title.replaceAll(
                        "[\\\\/:*?\"<>|]",
                        "_"
                );

        if (safe.length() > 100) {
            safe = safe.substring(0, 100);
        }

        ContentValues values =
                new ContentValues();

        values.put(
                MediaStore.Video.Media.DISPLAY_NAME,
                safe + ".mp4"
        );

        values.put(
                MediaStore.Video.Media.MIME_TYPE,
                "video/mp4"
        );

        values.put(
                MediaStore.Video.Media.RELATIVE_PATH,
                Environment.DIRECTORY_DOWNLOADS
        );

        ContentResolver resolver =
                getContentResolver();

        Uri uri =
                resolver.insert(
                        MediaStore.Video.Media.EXTERNAL_CONTENT_URI,
                        values
                );

        if (uri == null) {
            throw new Exception(
                    "تعذر إنشاء ملف الفيديو."
            );
        }

        try (
                InputStream in =
                        new FileInputStream(source);

                OutputStream out =
                        resolver.openOutputStream(uri)
        ) {

            byte[] buffer =
                    new byte[1024 * 1024];

            int n;

            while (
                    (n = in.read(buffer)) > 0
            ) {

                out.write(
                        buffer,
                        0,
                        n
                );
            }

            out.flush();
        }
    }

    private void finishSuccess(
            File workDir
    ) {

        deleteDirectory(workDir);

        runOnUiThread(() -> {

            progress.setVisibility(
                    View.GONE
            );

            download.setEnabled(true);

            status.setText(
                    "✅ تم التحميل بنجاح\n" +
                    "تم حفظ الفيديو في Download"
            );
        });
    }

    private void showError(
            String message
    ) {

        runOnUiThread(() -> {

            progress.setVisibility(
                    View.GONE
            );

            download.setEnabled(true);

            status.setText(
                    "❌ حدث خطأ أثناء التحميل\n\n" +
                    (
                            message == null
                                    ? "خطأ غير معروف"
                                    : message
                    )
            );
        });
    }

    private void deleteDirectory(
            File dir
    ) {if (dir == null ||
                !dir.exists()) {
            return;
        }

        File[] files =
                dir.listFiles();

        if (files != null) {

            for (File f : files) {

                if (f.isDirectory()) {

                    deleteDirectory(f);

                } else {

                    f.delete();
                }
            }
        }

        dir.delete();
    }
}
