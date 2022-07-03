import { createDbWorker } from "sql.js-httpvfs";
import $ from "cash-dom";
import * as echarts from "echarts/core";
import { BarChart } from "echarts/charts";
import { TitleComponent, TooltipComponent, GridComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

let worker;
echarts.use([
    BarChart,
    TitleComponent, TooltipComponent, GridComponent,
    CanvasRenderer
]);

const initDatabase = async () => {
    const workerUrl = new URL(
        "../node_modules/sql.js-httpvfs/dist/sqlite.worker.js",
        import.meta.url,
    );
    const wasmUrl = new URL(
        "../node_modules/sql.js-httpvfs/dist/sql-wasm.wasm",
        import.meta.url,
    );
    const config = {
        from: "inline",
        config: {
            serverMode: "full", // file is just a plain old full sqlite database
            requestChunkSize: 4096, // the page size of the  sqlite database (by default 4096)
            url: "/data.db" // url to the database (relative or full)
        }
    };
    let maxBytesToRead = 10 * 1024 * 1024;
    const worker = await createDbWorker(
        [config],
        workerUrl.toString(),
        wasmUrl.toString(),
        maxBytesToRead // optional, defaults to Infinity
    );
    return worker;
}

/**
 * 获取投票帖子
 * @returns {Promise<[any[]]>}
 */
const fetchVotePost = async () => {
    let result = await worker.db.exec("SELECT title, url, id FROM vote_post");
    return [...result[0].values]
}

/**
 * 渲染投票帖子
 * @param {[any[]]} posts 
 */
const renderVotePost = (posts) => {
    posts = posts
        .map(v => [v[0].replace(/【.+】/, ''), v[1], v[2]])
        .sort((a, b) => a[0].localeCompare(b[0]));
    let postsList = $(`
        <ul class="list">
            ${posts
            .map(post => `<li class="vote list-item" data-id="${post[2]}">${post[0]}</li>`)
            .join("\n")}
        </ul>
    `);
    let postListDiv = $("#post-list");
    postListDiv.children().remove();
    postListDiv.append(postsList);
}

/**
 * 获取投票帖子中的数据
 * @param {number} voteId 投票帖子 id 
 * @returns {Promise<[any[]]>}
 */
const fetchPlotData = async (voteId) => {
    let result = await worker.db.exec(`SELECT name, count FROM vote_item WHERE vote_id = ${voteId}`);
    return [...result[0].values]
}

/**
 * 根据数据渲染柱状图
 * @param {string} title 
 * @param {[any[]]} rawData 
 */
const plot = (title, rawData) => {
    rawData = rawData.sort((a, b) => a[1] - b[1]);
    let chartDom = document.getElementById("plot");
    let chart = echarts.init(chartDom);
    chart.setOption({
        title: {
            text: title,
            x: 'center',
            textAlign: 'center'
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        grid: {
            containLabel: true
        },
        yAxis: {
            type: "category",
            data: rawData.map(v => v[0]),
            axisTick: {
                alignWithLabel: true
            }
        },
        xAxis: {
            type: "value"
        },
        series: [
            {
                data: rawData.map(v => v[1]),
                type: 'bar',
                label: {
                    formatter: "{b}: {c}",
                    position: "right"
                }
            }
        ]
    });
}

const fetchAndPlot = async (title, voteId) => {
    let plotData = await fetchPlotData(voteId);
    plot(title, plotData);
}

(async () => {
    worker = await initDatabase();
    let votePosts = await fetchVotePost();
    renderVotePost(votePosts);
    $(".vote").on("click", (ev) => {
        let target = $(ev.currentTarget);
        fetchAndPlot(target.text(), target.data("id"));
    });
})();
